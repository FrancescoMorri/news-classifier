import numpy as np
from torch.utils.data import TensorDataset, DataLoader, SequentialSampler
from helpers import *
from scraping import *
from datetime import datetime
import streamlit as st
import pandas as pd
import json
from google.cloud import firestore
from google.oauth2 import service_account


def load_data_on_cloud(date, evaluation, key):
    db = firestore.Client(credentials=key, project="news-classifier-bb21e")

    doc_ref = db.collection("news-history").document("date-points")
    values = doc_ref.get().to_dict()['points']
    values.append(evaluation)

    doc_ref.update({u'points': values})
    doc_ref.update({u'date': firestore.ArrayUnion([date])})


def update_data_on_cloud(evaluation, key):
    db = firestore.Client(credentials=key, project="news-classifier-bb21e")

    doc_ref = db.collection("news-history").document("date-points")
    values = doc_ref.get().to_dict()['points']
    values[-1] = evaluation
    doc_ref.update({u'points': values})

def download_data_from_cloud(key):
    db = firestore.Client(credentials=key, project="news-classifier-bb21e")

    doc_ref = db.collection("news-history").document("date-points")

    return doc_ref.get().to_dict()



@st.cache
def load_model(model_path):
    model = BertClassifier()
    model.load_state_dict(torch.load(model_path,map_location=torch.device('cpu')))
    return model




st.set_page_config("news-classifier", page_icon="💲")

full_today_news = []
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
CNBC = get_CNBC()
REUTERS = get_REUTERS()
BSSN_STD = get_BSNN_STD()

if CNBC:
    full_today_news.extend(CNBC)
if REUTERS:
    full_today_news.extend(REUTERS)
if BSSN_STD:
    full_today_news.extend(BSSN_STD)

found_news = False

hist_data = download_data_from_cloud(creds)

last_date = hist_data['date'][-1]
today_flag = False
today_econ_val = 0

if (last_date.date() - datetime.today().date()).days == 0:
    today_flag = True
    today_econ_val = hist_data['points'][-1]



st.header("Economic News Classifier")

st.caption("This app scrapes three news website (CNBC, Reuters, Business Standard) and uses a fine-tuned Bert model to classify the news.")
st.caption("A news is either 1 (positive), 0 (neutral) or -1 (negative). Then it outputs the mean of all the news founded, as an indicator of today economic state.")
st.caption("Also it saves on a cloud database the results of the day, plotting every time a graph showing the data history.")


st.subheader("Scraping News")
with st.form('Scraping News'):
    n = len(full_today_news)
    if n == 0:
        st.warning("No news today!!")
    elif n>0:
        st.success("Found %d news today!!"%n)
        found_news = True
    
    submitted = st.form_submit_button("Continue")

if submitted:
    if found_news:

        inputs, masks = preprocessing_for_bert(full_today_news)

        dataset = TensorDataset(inputs, masks)
        sampler = SequentialSampler(dataset)
        dataloader = DataLoader(dataset, sampler=sampler, batch_size=1)

        with st.spinner("Loading model..."):
            model = load_model('bert_classifier.pt')

        probs = bert_predict(model, dataloader)
        labels = [gen_labels(np.argmax(p)) for p in probs]
        points = [give_points(np.argmax(p)) for p in probs]
        classified_news = pd.DataFrame()
        classified_news['news'] = full_today_news
        classified_news['label'] = labels
        classified_news['points'] = points
        final_val = np.mean(points)

        if today_flag:
            if final_val == today_econ_val:
                pass
            else:
                update_data_on_cloud(final_val, creds)
        else:
            load_data_on_cloud(datetime.now(), final_val, creds)

        st.subheader("The evaluation of today economic situation is:")
        st.write(final_val)
        st.subheader("Historical data:")
        plot_data = pd.DataFrame(download_data_from_cloud(creds))
        plot_data['date'] = plot_data['date'].dt.strftime('%d %m %Y')
        st.line_chart(plot_data, x='date', y='points')

        st.subheader("and all the news found:")
        st.dataframe(classified_news)


    else:
        st.info("No news, no predictions, try later ;) (still get the historical data)", icon="❗")
        plot_data = pd.DataFrame(download_data_from_cloud(creds))
        plot_data['date'] = plot_data['date'].dt.strftime('%d %m %Y')
        st.line_chart(plot_data, x='date', y='points')



