import glob
import streamlit as st
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import ChatMessage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.prompts import load_prompt
from PIL import Image
import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOllama 

# 사용할 키로 등록.
st.set_page_config(page_title="PROMPT GENIE 💬", page_icon="💬")
img = Image.open("images/img1.jpg")
st.image(img, width=256)
st.title("PROMPT GENIE 💬")
st.subheader("by MIRACOM-INC")
USE_OPENAI = True

if "messages" not in st.session_state:
    st.session_state["messages"] = []


def print_history():
    for msg in st.session_state["messages"]:
        st.chat_message(msg.role).write(msg.content)


def add_history(role, content):
    st.session_state["messages"].append(ChatMessage(role=role, content=content))


# 체인을 생성합니다.
def create_chain(prompt, model):
    # 기존코드
    #chain = prompt | ChatOpenAI(model_name=model) | StrOutputParser()
    if USE_OPENAI is True:
        load_dotenv()
        if os.getenv('OPENAI_API_KEY') is None:
            raise ValueError('OPENAI_API_KEY environment variable is not set')
        st.secrets["OPENAI_API_KEY"]
        chain = prompt | ChatOpenAI(model_name=model) | StrOutputParser()
    else:
        llm = ChatOllama(model="exaone-3.8B:latest")
        chain = prompt | llm | StrOutputParser()
    return chain


with st.sidebar:
    # openai_api_key = st.text_input(
    #     "OpenAI API Key", value="", key="api_key", type="password"
    # )
    # key_btn = st.button("키 설정하기", key="apply_api_key_btn")
    # if key_btn:
    #     os.environ["OPENAI_API_KEY"] = openai_api_key
    #     st.write("설정이 완료되었습니다")
    #     USE_OPENAI = True

    agree = st.checkbox("Use OpenAI (GPT Series)")
    if agree:
        USE_OPENAI = True
    else:
        USE_OPENAI = False

    clear_btn = st.button("대화내용 초기화")
    tab1, tab2, tab3 = st.tabs(["프롬프트", "프리셋", "프롬프트 메이커"])
    prompt = """당신은 친절한 AI 어시스턴트 입니다. 사용자의 질문에 간결하게 한글로 답변해 주세요."""
    user_text_prompt = tab1.text_area("프롬프트", value=prompt)
    user_text_apply_btn = tab1.button("프롬프트 적용", key="apply1")

    if user_text_apply_btn:
        tab1.markdown(f"✅ 프롬프트가 적용되었습니다!")
        if USE_OPENAI is True:
            load_dotenv()
            if os.getenv('OPENAI_API_KEY') is None:
                raise ValueError('OPENAI_API_KEY environment variable is not set')
            #st.secrets["OPENAI_API_KEY"]
            prompt_template = user_text_prompt + "\n\n#Question:\n{question}\n\n#Answer:"
            prompt = PromptTemplate.from_template(prompt_template)
            st.session_state["chain"] = create_chain(prompt, "gpt-4o")
        else:
            llm = ChatOllama(model="EEVE-Korean-10.8B:latest")
        
            prompt = ChatPromptTemplate.from_template(
                "다음의 질문에 간결하게 답변해 주세요:\n{question}"
            )
            chain = prompt | llm | StrOutputParser()
            st.session_state["chain"] = chain


            
        # prompt_template = user_text_prompt + "\n\n#Question:\n{question}\n\n#Answer:"
        # prompt = PromptTemplate.from_template(prompt_template)
        # st.session_state["chain"] = create_chain(prompt, "gpt-4o")

    prompt_files = glob.glob("prompts/*.yaml")
    prompt_filenames = [file.split("/")[-1].split(".")[0] for file in prompt_files]
    user_selected_prompt = tab2.selectbox("프리셋 선택", prompt_filenames)
    user_selected_apply_btn = tab2.button("프롬프트 적용", key="apply2")

    if user_selected_apply_btn:
        tab2.markdown(f"✅ 프롬프트가 적용되었습니다!!")
        # 기존코드 경로 에러
        #prompt = load_prompt(f"prompts/{user_selected_prompt}.yaml", encoding="utf8")
        prompt = load_prompt(f"{user_selected_prompt}.yaml", encoding="utf8")
        # task 에러
        task = "프롬프트 전문가"
        tab2.markdown(prompt)
        #기존코드
        #st.session_state["chain"] = create_chain(prompt, "gpt-4o")
        prompt_maker = prompt.partial(task=task)
        st.session_state["chain"] = create_chain(prompt_maker, "gpt-4o")

    prompt_maker = load_prompt(f"prompts/프롬프트.yaml", encoding="utf8")
    task = tab3.text_input("task")
    user_prompt_apply_btn = tab3.button("프롬프트 적용", key="apply3")
    if user_prompt_apply_btn:
        tab3.markdown(f"✅ 프롬프트가 적용되었습니다")
        prompt_maker = prompt_maker.partial(task=task)
        st.session_state["chain"] = create_chain(prompt_maker, "gpt-4o")

if clear_btn:
    retriever = st.session_state["messages"].clear()

print_history()


if "chain" not in st.session_state:
    # user_prompt
    prompt_template = user_text_prompt + "\n\n#Question:\n{question}\n\n#Answer:"
    prompt = PromptTemplate.from_template(prompt_template)
    
    # OpenAI 선택 
    # apikey 에러나서 수정
    if USE_OPENAI is True:
        load_dotenv()
        if os.getenv('OPENAI_API_KEY') is None:
            raise ValueError('OPENAI_API_KEY environment variable is not set')
        st.session_state["chain"] = create_chain(prompt, "gpt-3.5-turbo")
    else:
        #llm = ChatOllama(model="exaone-3.8B:latest")
        llm = ChatOllama(model="EEVE-Korean-10.8B:latest")
        prompt = ChatPromptTemplate.from_template(
            "다음의 질문에 간결하게 답변해 주세요:\n{question}"
        )
        chain = prompt | llm | StrOutputParser()
        st.session_state["chain"] = chain

if user_input := st.chat_input():
    add_history("user", user_input)
    st.chat_message("user").write(user_input)

    with st.chat_message("assistant"):
        chat_container = st.empty()

        stream_response = st.session_state["chain"].stream(
            {"question": user_input}
        )  # 문서에 대한 질의
        ai_answer = ""
        for chunk in stream_response:
            ai_answer += chunk
            chat_container.markdown(ai_answer)
        add_history("ai", ai_answer)
