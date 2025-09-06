from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.template import loader
# from .forms import FileUploadForm
from .models import SyncStatus, Compliances_Model, DocumentsModel, DocumentSync
from django.http import JsonResponse

from datetime import datetime
import json
from django.db.models import Q

import uuid
from sklearn.metrics.pairwise import cosine_similarity
from functools import lru_cache

import pandas as pd
from django.db.models import Case, When

from django.utils import timezone
from datetime import timedelta

from .utils.comp_getter import comp_fetch_and_extract, is_good_compliance_date_check
from .utils.invoice_extractor import extract_invoice_data

from django.contrib.auth.decorators import login_required

import faiss
import os
from sentence_transformers import SentenceTransformer
import timeit
from pdf2image import convert_from_path
import pytesseract
import numpy as np

from .utils.bank_graph import plot_bar_graph, plot_distribution_graph, plot_pie_chart
from .utils.bank_anomalies import find_anomalies_df, find_duplicates_df, bounced_df
from .utils.tds_section import get_tds_section_details

from PIL import Image
import io

import matplotlib
from loguru import logger

logger.add('main_dev.log')

### MODEL FOR MAKING EMBEDDINGS
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

pt= r'C:\Users\os\Desktop\ca_sahib\poppler-24.08.0\Library\bin'
matplotlib.use("Agg")  # ✅ Non-GUI backend


@lru_cache(maxsize=128)
def get_tag_embedding(tag: str):
    return model.encode(tag, normalize_embeddings=True)
"""
Input:
- PDF/Scanned Invoice(s) or ZIP of multiple invoices

Process:
- OCR & text extraction
- Extract invoice number, GSTIN, date, amounts, HSN code
- Validate GSTIN structure, date, tax consistency

Output:
- Tabular invoice summary
- Flags for missing fields or mismatches
- Export as Excel

Optional: Verify GSTIN via public API
"""

from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.template import loader
# from .forms import SignUpForm
from .models import SyncStatus, Compliances_Model, DocumentsModel, DocumentSync, Clients

from datetime import datetime
from django.db.models import Q
import uuid
from sklearn.metrics.pairwise import cosine_similarity
from functools import lru_cache

from .utils.comp_getter import comp_fetch_and_extract, is_good_compliance_date_check

from django.contrib.auth import login

from django.contrib.auth.decorators import login_required

import faiss
from sentence_transformers import SentenceTransformer
import timeit
from pdf2image import convert_from_path

import pytesseract
import numpy as np

from .utils.bank_anomalies import find_anomalies_df, find_duplicates_df, bounced_df

# from .forms import SignUpForm


### MODEL FOR MAKING EMBEDDINGS
# model = SentenceTransformer('paraphrase-MiniLM-L6-v2')


@lru_cache(maxsize=128)
def get_tag_embedding(tag: str):

    return model.encode(tag, normalize_embeddings=True)
"""
Input:
Optional: Verify GSTIN via public API
"""

def clients(request):
    if request.method == 'POST':
        obj = Clients.objects.create(
            ca_id=request.user,
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            contact=request.POST.get("contact"),
            address=request.POST.get("address"),
            business_name=request.POST.get("business_name"),
            business_type=request.POST.get("business_type"),
            gst_number=request.POST.get("gst_number"),
            pan_number=request.POST.get("pan_number")
        )
        obj.save()
        

    objs = Clients.objects.filter(ca_id = request.user)
    return render(request, 'clients.html', context={'clients' : objs})

def front_page(request):
    return render(request, 'front_page.html')


def front_page2(request):
    messages.success(request, f'Click anywhere to go to home page!!')
    return render(request, 'front_page2.html')


def ask_ca_ai(request):
    return render(request, 'ask_ca_ai.html')


# TDS PART
def tds(request):
    # "Later continure to this webiste :- https://incometaxindia.gov.in/Pages/tools/tds-calculator.aspx"
    if request.method == 'POST':
        logger.info('got post')
        # description = request.POST.get('description')
        data = json.loads(request.body)
        description = data.get("description", "").strip()

        logger.info(f'got the description:- {description}', )
        try:
            section, details = get_tds_section_details(description)
        except Exception as e:
            logger.error(f"Error getting TDS section details: {e}")
            return JsonResponse({"success": False, "error": "Error processing the request."})
        
        # return render(request, 'tds.html', context={'section': section, 'details': details, 'description': description})

        logger.info(f'section:- {section}, details:- {details}')
        return JsonResponse({"success": True, 'section': section, 'details': details})
    
    return render(request, 'tds.html')


# Create your views here.
def home(request):
    return render(request, 'home.html')

# function to input the imgs and start analysing
@login_required
def invoice_input(request):
    return render(request, 'invoice_input.html')

@login_required
def invoice_process(request):
    if request.method == 'POST':
        file = request.FILES.get('invoice_file')
        obj = DocumentsModel.objects.create(file = file)
        logger.info("File uploaded successfully")
        # logger.info(file.content_type)
        # logger.info(type(file))
        # logger.info(file)
        # return redirect('upload_success')  # optional success page

        img = Image.open(file)
        # Save the image to a BytesIO object in a specific format
        byte_arr = io.BytesIO()
        img.save(byte_arr, format='PNG') # Or 'JPEG', 'GIF', etc.
        image_bytes = byte_arr.getvalue()

        # logger.info(type(image_bytes))

        data_json = extract_invoice_data(image_bytes)

        # Make sure DataFrame is well-formed
        if isinstance(data_json, dict):
            df = pd.DataFrame([data_json])
        else:
            df = pd.DataFrame(data_json)


        html_df = df.to_html(
            classes=(
                "min-w-full table-auto text-sm text-left text-gray-700 "
                "border border-gray-200 divide-y divide-gray-100"
),
            # classes="table table-bordered", 
            index=False, 
            border=1, 
            justify='left'
        )

        logger.info(f"Done processing invoice, {html_df}, DATAFRAME : {df}")

        return render(request, 'invoice_process.html', context={'data_json': data_json, 'html_df': html_df})
        
        
    return render(request, 'invoice_process.html', {})

@login_required
def compliance(request):
    sync_obj, created = SyncStatus.objects.get_or_create(name='compliance_shc')

    if created or timezone.now() - sync_obj.last_fetched > timedelta(weeks=1):
        all_compliance_json = comp_fetch_and_extract()
        sync_obj.last_fetched = timezone.now()
        sync_obj.save()

        # Track which objects are still valid
        valid_pks = []

        for i in all_compliance_json:
            corrected_month = datetime.strptime(i['month'].lower(), "%B").month
            if is_good_compliance_date_check(int(i['date']), int(corrected_month), int(i['year'])):
                obj, _ = Compliances_Model.objects.update_or_create(
                    description=i['description'],
                    date=i['date'],
                    month=corrected_month,
                    year=i['year'],
                    defaults={
                        # add other fields to update if needed
                    }
                )
                obj.save()
                valid_pks.append(obj.id)

        # Delete only those not in the latest data
        Compliances_Model.objects.exclude(pk__in=valid_pks).delete()

    objs = Compliances_Model.objects.all()
    sync_obj = SyncStatus.objects.get(name='compliance_shc')
    return render(request, 'compliance.html', context={'models': objs, 'total_compliances': len(objs), 'sync_obj':sync_obj })

@login_required
def mark_complete(request, id):
    compliance = get_object_or_404(Compliances_Model, id=id)
    compliance.completed = True
    compliance.save()

    sync_obj = SyncStatus.objects.get(name='compliance_shc')
    sync_obj.completed_number += 1
    sync_obj.save()

    return redirect('compliance')  # or your compliance page name

@login_required
def documents(request):
    all_objs = DocumentsModel.objects.all()
    COUNT_ALL_DOCS = len(all_objs)
    COUNT_INVOICES = len(DocumentsModel.objects.filter(doc_type = 'invoice'))
    COUNT_LEDGER = len(DocumentsModel.objects.filter(doc_type = 'ledger'))
    COUNT_OTHERS = len(DocumentsModel.objects.filter(doc_type = 'others'))
    
    if request.method == 'POST':
        if 'upload_doc' in request.POST:
            logger.info("uploaded file")
            fil = request.FILES.get('doc_upload')
            obj = DocumentsModel.objects.create(file = fil)
            obj.save()

            pdf_path = obj.file.path
            pages = convert_from_path(pdf_path, dpi=300, poppler_path = pt) # dpi can be adjusted for better accuracy
            
            extracted_text = ''
            for page in pages:
                text = pytesseract.image_to_string(page)
                extracted_text += text + '\n'

            embedding = model.encode(extracted_text)

            tags = ["invoice", "ledger", 'others']
            tag_embeddings = [get_tag_embedding(tag) for tag in tags]
            similarities = cosine_similarity([embedding], tag_embeddings)[0]
            obj.doc_type = tags[similarities.argmax()]  # assign highest match



            doc_obj, created = DocumentSync.objects.get_or_create(name = 'vector_index.faiss')
            if created:
                # Initialize FAISS
                index = faiss.IndexFlatL2(doc_obj.embedding_dim)

            else:
                index = faiss.read_index(doc_obj.name)

            faiss_index = index.ntotal
            index.add(np.array([embedding]))
            doc_obj.d[faiss_index] = str(obj.id)
            faiss.write_index(index, doc_obj.name)
            logger.info("Done uplaoding process")
            
            # obj.save()
            doc_obj.save()

        # elif 'semantic_search' in request.POST :
        #     # handle searching
        #     logger.info('kejb')
        #     logger.info(f"searched for : {request.POST.get('search')}")

    elif request.method == 'GET'  and 'semantic_search' in request.GET:
        # logger.info('kejb')
        logger.info(f"searched for : {request.GET.get('search')}")
        query = request.GET.get('search')
        obj = DocumentSync.objects.get(name = 'vector_index.faiss')

        index = faiss.read_index(obj.name)
        search = model.encode(query)
        D,I = index.search(np.array([search]), k = min([5, COUNT_ALL_DOCS]))
        logger.info(f"{D}, {I}")

        d = dict(obj.d)

        final_lst = []
        logger.info(d)

        # Zip distances and indices together, and sort by distance
        results = sorted(zip(D[0], I[0]), key=lambda x: x[0])

        for dist, idx in results:
            if idx == -1:
                continue
            idx_str = str(idx)
            if idx_str in d:
                final_lst.append(uuid.UUID(d[idx_str]))

        logger.info(final_lst)
        # logger.info(final_lst)

        all_objs = DocumentsModel.objects.filter(id__in = final_lst)
        
        # Preserve order using Case/When
        preserved_order = Case(*[When(id=val, then=pos) for pos, val in enumerate(final_lst)])
        all_objs = all_objs.order_by(preserved_order)

        logger.info(len(all_objs))
    return render(request, 'documents.html', context = {
        'objs' : all_objs, 
        'COUNT_ALL_DOCS' : COUNT_ALL_DOCS,
        'COUNT_INVOICES' : COUNT_INVOICES,
        "COUNT_LEDGER" : COUNT_LEDGER,
        "COUNT_OTHERS" : COUNT_OTHERS
        }
    )


@login_required
def bank_statement_analyzer(request):
    return render(request, 'bank_statement_analyzer.html', context={})

@login_required
def bank_statement_analyzer_process(request):
    if request.method == 'POST':
        file = request.FILES.get('bank_statement_file')

        # this time we won't create any model object but will just simply analyze and return the results to the user
        data = pd.read_csv(file)

        ################ LEDGER WILL BE HERE ONLY
        d = dict(data['name'].value_counts())
        final = {}

        for i in d:
            j = d[i]
            if j.item() > 1:
                final[i] = int(j)

        logger.info(final)

        # lets make ledger for each of these
        ls = []

        for i in final:
            ls.append(data[data['name'] == i].to_html(
                classes=(
                    "min-w-full table-auto text-sm text-left text-gray-700 "
                    "border border-gray-200 divide-y divide-gray-100"
                ),
                # classes="table table-bordered", 
                index=False, 
                border=1, 
                justify='left'
                )
                )
        
        bounced_data = bounced_df(data)

        ## GETTING GRAPHS
        context = {
            'bar' : plot_bar_graph(data),
            'pie' : plot_pie_chart(data), 
            'distribution' : plot_distribution_graph(data),

            'duplicates_df' : find_duplicates_df(data).to_html(
                # classes="table table-bordered", 
                classes=(
                    "min-w-full table-auto text-sm text-left text-gray-700 "
                    "border border-gray-200 divide-y divide-gray-100"
                ),
                index=False, border=1, justify='left'),

            'anomalies' : find_anomalies_df(data).to_html(
                # classes="table table-bordered", 
                classes=(
                    "min-w-full table-auto text-sm text-left text-gray-700 "
                    "border border-gray-200 divide-y divide-gray-100"
                ),
                index=False, border=1, justify='left'),

            'bounced_df' :bounced_data.to_html(
                # classes="table table-bordered", 
                classes=(
                    "min-w-full table-auto text-sm text-left text-gray-700 "
                    "border border-gray-200 divide-y divide-gray-100"
                ),
                index=False, border=1, justify='left'),

            'ledger' : ls,

            'len_bounced' : len(bounced_data) > 0
        }

    
    return render(request, 'bank_statement_analyzer_process.html', context= context)

# def compliance(request):
#     # website for compliance calendar :- https://eztax.in/tax-compliance-calendar-it-tds-gst-roc
#     # think if we want to fetch or just get it once a year
#     sync_obj, created = SyncStatus.objects.get_or_create(name='compliance_shc')

#     if created or timezone.now() - sync_obj.last_fetched > timedelta(weeks=1):
#         # Fetch the data
#         all_compliance_json = comp_fetch_and_extract()

#         # Update last fetched time
#         sync_obj.last_fetched = timezone.now()
#         sync_obj.save()

#         # now we want to remove all modedls and create the new ones
#         all_objs = Compliances_Model.objects.all()
#         all_objs.delete()

#         # now lets create model
#         for i in all_compliance_json:
#             corrected_month = datetime.strptime(i['month'].lower(), "%B").month
#             if is_good_compliance_date_check(int(i.date), int(corrected_month), int(i.year))
#                 # lets now create the object
#                 Compliances_Model.objects.create(
#                     description = i.description,
#                     date = i.date,
#                     month = corrected_month,
#                     year = i.year
#                 )
#     objs = Compliances_Model.objects.all()
#     return render(request, 'compliance.html', context= {'models' : objs, 'total_compliances' : len(objs)})

from .forms import ProfileForm

@login_required
def profile(request):
    """
    Displays the user profile page.
    """
    profile = request.user.profile
    form = ProfileForm(request.POST or None, instance=profile)
    if form.is_valid():
        form.save()
        return redirect('profile')

    return render(request, 'profile.html')


from .forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

def register(request):
    logger.info("got request")
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        logger.info("got post")
        if form.is_valid():
            logger.info('is valid')
            form.save()
            # username = form.cleaned_data.get('username')
            # email = form.cleaned_data.get('email')
            # ######################### mail system #################################### 
            # htmly = get_template('user/Email.html')
            # d = { 'username': username }
            # subject, from_email, to = 'welcome', 'your_email@gmail.com', email
            # html_content = htmly.render(d)
            # msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            # msg.attach_alternative(html_content, "text/html")
            # msg.send()
            # ################################################################## 
            messages.success(request, f'Your account has been created ! You are now able to log in')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form, 'title':'register here'})
 
################ login forms################################################### 
def Login(request):
    if request.method == 'POST':
 
        # AuthenticationForm_can_also_be_used__
 
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username = username, password = password)
        if user is not None:
            form = login(request, user)
            messages.success(request, f' welcome {username} !!')
            return redirect('home')
        else:
            messages.info(request, f'account done not exit plz sign in')
    form = AuthenticationForm()
    return render(request, 'login.html', {'form':form, 'title':'log in'})

# It's also a good idea to protect your existing views.
# For example, the view that renders bank_statement_analyzer_process.html
# should probably require a user to be logged in.
# @login_required
# def bank_statement_analyzer_process(request):
#     ... your view logic ...

