import streamlit as st, pandas as pd, requests, os
from functions import *
# from nltk.stem import WordNetLemmatizer
# Load environment variables

@st.experimental_memo(suppress_st_warning=True, show_spinner=False)
def get_cred_config():
    secret = os.environ.get("GCP_API_URL")
    if secret:
        print("GCP_API_URL found in environment variables")
        return secret
    else:
        print("GCP_API_URL not found in environment variables")
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv("API_URL")

@st.experimental_memo(suppress_st_warning=True, show_spinner=False)
def analyse(text):
    # Lemmatize
    # lemmatizer = WordNetLemmatizer()
    # text = lemmatizer.lemmatize(text)

    # Analyse the text
    api = get_cred_config()
    headers = {'Content-Type': 'application/json'}
    prediction = requests.post(api, json={"text": text}, headers=headers).json()['predictions']
    prediction2 = requests.post(api, json={'text2': text}, headers=headers).json()['predictions']
    classes = requests.post(api, json={'classes': True}, headers=headers).json()['classes']

    # Create a dataframe
    dic = {}
    for i in range(len(classes)):
        dic[i] = classes[i]
    df = pd.DataFrame(prediction, columns=classes)

    # Display the top 3 predictions and their probabilities
    df = df.T
    df.columns = ['Probability']
    df = df.sort_values(by='Probability', ascending=False)
    df['Probability'] = df['Probability'].apply(lambda x: str(round(x*100, 2)) + '%')
    df = df.reset_index().rename(columns={'index': 'Job Title'})
    df['Job Title'] = df['Job Title'].str.title()

    return df, prediction2

@st.experimental_memo(suppress_st_warning=True, show_spinner=False)
def show_importance():
    return pd.read_csv('Backend/imp_minmax.csv')

@st.experimental_memo(suppress_st_warning=True, show_spinner=False)
def show_dataframe():
    df = pd.read_csv('Backend/df_stack.csv', index_col=0)
    df.index = df.index.str.title()
    fields = list(map(lambda x: x.title() if x not in  ['HR','BPO'] else x.upper(), df.columns))
    return df, fields

# App UI
if __name__ == '__main__':
    st.set_page_config(page_title='Resume Analyzer by Guidesify', layout="wide")
    st.markdown(read_text('./Text/hide_table_sn.txt'), unsafe_allow_html=True)
    st.markdown(read_text('./Text/hide_streamlit_menu.txt'), unsafe_allow_html=True) 
    st.sidebar.title("Select Option")
    option = st.sidebar.selectbox('', ['Main', 'About Models'])

    # Main Page
    if option == 'Main':
        st.title("Resume ML Model")
        st.caption("Version: " + "0.0.2")
        st.write("Although we will not store your resume, feel free to mask out any personal information.")

        # Create file uploader
        uploaded_file = st.file_uploader('Upload a file', type=['pdf'])
        if uploaded_file is not None:
            with st.spinner('Calling API...'):
                st.session_state.text = extract_resume(uploaded_file)
                s_result, v_result = analyse(st.session_state.text)
                st.code('Using a Stacking Classifier (F1 Score = 0.81), the top 3 predictions are:', language=None)
                st.dataframe(s_result.head(3))
                for i in range(2): 
                    st.text("")
                if st.button('Other Models'):
                    st.code('Using a hard Voting Classifier (F1 Score = 0.82), your resume is most suited in the {} field.'.format(v_result[0].title()), language=None)
    
    # About Page
    elif option == 'About Models':
        # About Stacking
        st.title("Stacking Classifier")
        st.write("The StackingClassifier is a meta-estimator that fits base classifiers each on the whole dataset. It then uses these base classifiers to build a new dataset which is used as the input to a meta-classifier. The meta-classifier is trained on this new dataset.")
        st.vega_lite_chart(show_importance(), {
            'mark': 'bar',
            'height': 300,
            'encoding': {
                'y': {'field': 'Model', 'type': 'nominal', 'sort': '-x'},
                'x': {'field': 'Importance', 'type': 'quantitative', 'axis': {'format': '%'}},
                'color': {'field': 'Model', 'type': 'nominal', 'legend': None},
                'tooltip': [{'field': 'Model', 'type': 'nominal'}, {'field': 'Importance', 'type': 'quantitative','format': '.2%'}],
            },
        }, use_container_width=True)

        st.subheader('Top 10 Features for each field')
        with st.spinner('Computing features...'):
            st.session_state.df_stack, st.session_state.fields = show_dataframe()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.session_state.field = st.selectbox('', st.session_state.fields)
            st.dataframe(
                st.session_state.df_stack[st.session_state.field.upper()]
                .sort_values(ascending=False).head(10).to_frame()
                .rename(columns={st.session_state.field.upper(): 'Importance'}), height=400
            )

        # About Voting
        for i in range(3): 
            st.text("")
        if st.button('Other Models'):
            st.title('Voting Classifier')
            st.write("The VotingClassifier is an ensemble-learning meta-classifier for classification which fits base classifiers each on the whole dataset. It, then, aggregates the individual predictions to form a final prediction. The predictions of each classifier are weighted by their accuracy on the given dataset.")
            st.write("For this model, the weights of the votes are uniform.")


