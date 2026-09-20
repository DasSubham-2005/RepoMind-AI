import io
import os
import re
import json
import sqlite3
import hashlib
import secrets
import html
import zipfile
from pathlib import Path

import numpy as np
import faiss
import streamlit as st
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="RepoMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    r"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root{
  --bg:#020713;
  --bg2:#061126;
  --panel:#071327;
  --panel2:#0a1931;
  --line:#17355f;
  --line2:#24549a;
  --text:#f6f8ff;
  --muted:#8ea6c9;
  --blue:#2b7fff;
  --cyan:#25d7ff;
  --purple:#8b5cf6;
  --green:#25df9a;
}

html,
body,
[class*="css"]{
  font-family:"Inter",sans-serif;
}

.stApp{
  color:var(--text);
  background:
    radial-gradient(
      700px 420px at 12% -8%,
      rgba(62,75,255,.18),
      transparent 65%
    ),
    radial-gradient(
      700px 500px at 100% 8%,
      rgba(0,205,255,.09),
      transparent 68%
    ),
    linear-gradient(
      180deg,
      #020713 0%,
      #030916 55%,
      #020610 100%
    );
}

#MainMenu,
footer{
  visibility:hidden;
}

header[data-testid="stHeader"]{
  background:rgba(2,7,18,.72);
  backdrop-filter:blur(14px);
}

[data-testid="stSidebar"]{
  background:
    linear-gradient(
      180deg,
      #030a18 0%,
      #020711 100%
    );
  border-right:1px solid rgba(45,84,145,.45);
}

[data-testid="stSidebar"]>div:first-child{
  padding:16px 12px 12px;
}

.sidebar-brand{
  padding:4px 8px 16px;
}

.sidebar-brand-title{
  font-size:1.02rem;
  font-weight:800;
  letter-spacing:-.035em;
}

.sidebar-dot{
  display:inline-block;
  width:8px;
  height:8px;
  border-radius:50%;
  background:#25d7ff;
  box-shadow:0 0 14px #25d7ff;
  margin-right:8px;
}

.sidebar-sub{
  color:#6f89af;
  font-size:.58rem;
  margin-top:5px;
}

.user-card{
  padding:12px 13px;
  border-radius:13px;
  border:1px solid #1a3b70;
  background:
    linear-gradient(
      145deg,
      rgba(20,50,99,.45),
      rgba(5,18,39,.72)
    );
}

.user-name{
  font-weight:800;
  font-size:.83rem;
}

.user-email{
  color:#829ac0;
  font-size:.61rem;
  margin-top:4px;
  word-break:break-all;
}

.user-note{
  color:#5f7da6;
  font-size:.57rem;
  margin-top:5px;
}

.chat-list-title{
  font-size:.76rem;
  font-weight:800;
  color:#dce7f9;
  margin:18px 4px 8px;
}

.sidebar-divider{
  height:1px;
  background:#152c4d;
  margin:18px 0;
}

.sidebar-section{
  font-size:.76rem;
  font-weight:800;
  color:#dce7f9;
  margin:4px 4px 8px;
}

.main-shell{
  width:100%;
  margin:0;
  padding:0 0 34px;
}

[data-testid="stAppViewContainer"] .main .block-container{
  max-width:1120px;
  padding:28px 34px 48px;
  margin:0 auto;
}

.hero{
  text-align:center;
  padding:22px 10px 18px;
}

.hero-kicker{
  font-size:.62rem;
  font-weight:800;
  letter-spacing:.18em;
  color:#9a8cff;
  margin-bottom:8px;
  text-transform:uppercase;
}

.hero-title{
  font-size:clamp(2.7rem,5vw,4rem)!important;
  line-height:1!important;
  font-weight:800;
  letter-spacing:-.07em!important;

  background:
    linear-gradient(
      90deg,
      #f8fbff 8%,
      #dce5ff 35%,
      #a88cff 66%,
      #29dfff 100%
    );

  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;

  margin:0!important;
}

.hero-sub{
  font-size:.88rem;
  color:#8fa9cd;
  margin-top:9px;
}

.hero-pills{
  display:flex;
  justify-content:center;
  gap:8px;
  flex-wrap:wrap;
  margin-top:13px;
}

.hero-pill{
  padding:6px 11px;
  border:1px solid #21457d;
  border-radius:999px;
  background:rgba(7,23,47,.72);
  color:#dce7fa;
  font-size:.61rem;
  font-weight:700;
}

.panel{
  border:1px solid #18375f;
  border-radius:17px;

  background:
    linear-gradient(
      145deg,
      rgba(7,20,42,.94),
      rgba(3,11,25,.96)
    );

  box-shadow:
    0 14px 40px rgba(0,0,0,.18),
    inset 0 1px 0 rgba(255,255,255,.025);
}

.upload-panel{
  padding:20px 20px 14px;
}

.panel-head{
  display:flex;
  align-items:center;
  gap:12px;
  margin-bottom:13px;
}

.panel-icon{
  width:40px;
  height:40px;
  border-radius:12px;

  display:flex;
  align-items:center;
  justify-content:center;

  background:
    linear-gradient(
      135deg,
      #176fff,
      #783cff
    );

  box-shadow:0 0 22px rgba(67,103,255,.22);

  font-size:1.15rem;
}

.panel-title{
  font-size:.94rem;
  font-weight:800;
}

.panel-sub{
  font-size:.63rem;
  color:#7693ba;
  margin-top:3px;
}

.section-row{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
  margin:18px 0 9px;
}

.section-title{
  font-size:.86rem;
  font-weight:800;
  color:#f4f7ff;
}

.section-note{
  font-size:.59rem;
  color:#6785ad;
}

.workspace{
  padding:14px 16px;
  border:1px solid #193b6b;
  border-radius:14px;
  background:rgba(5,17,36,.72);
}

.workspace-head{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:16px;
}

.workspace-name{
  font-size:.78rem;
  font-weight:800;
}

.workspace-note{
  font-size:.59rem;
  color:#708db4;
  margin-top:4px;
}

.metrics{
  display:flex;
  gap:7px;
  flex-wrap:wrap;
  justify-content:flex-end;
}

.metric{
  min-width:70px;
  padding:7px 9px;
  text-align:center;

  border:1px solid #17365f;
  border-radius:9px;

  background:rgba(2,10,23,.72);
}

.metric-label{
  font-size:.47rem;
  color:#6986aa;
  font-weight:800;
  letter-spacing:.08em;
}

.metric-value{
  font-size:.76rem;
  font-weight:800;
  margin-top:2px;
}

.ready{
  color:#5eeeb5;
}

.mode-strip{
  display:grid;
  grid-template-columns:repeat(4,minmax(0,1fr));
  gap:10px;
  margin:10px 0 18px;
  width:100%;
}

.mode-card{
  min-width:0;
  padding:13px 14px;

  border:1px solid #16345d;
  border-radius:13px;

  background:
    linear-gradient(
      145deg,
      rgba(7,21,43,.78),
      rgba(3,12,27,.82)
    );

  box-sizing:border-box;
}

.mode-card:hover{
  border-color:#2a5da1;
  transform:translateY(-1px);
  transition:.18s ease;
}

.mode-icon{
  font-size:1rem;
}

.mode-name{
  font-size:.61rem;
  font-weight:800;
  margin-top:4px;
}

.mode-text{
  font-size:.52rem;
  color:#6684aa;
  margin-top:2px;
}

.chat-panel{
  border:1px solid #18375f;
  border-radius:17px;

  background:
    linear-gradient(
      145deg,
      rgba(6,18,38,.72),
      rgba(2,9,20,.84)
    );

  padding:14px;
}

.chat-top{
  display:flex;
  align-items:center;
  justify-content:space-between;
  margin-bottom:10px;
}

.chat-title{
  font-size:.82rem;
  font-weight:800;
}

.chat-status{
  font-size:.57rem;
  color:#5fdcae;
}

.stChatMessage{
  border:1px solid rgba(25,56,96,.55);
  border-radius:12px;
  background:rgba(4,14,29,.62);
}

.stChatMessage p,
.stChatMessage li,
.stChatMessage span,
.stChatMessage div{
  color:#E5E7EB !important;
}

.evidence-code{
  font:.57rem/1.5 ui-monospace,
  SFMono-Regular,
  Consolas,
  monospace;

  color:#F1F5F9;
  white-space:pre-wrap;
}

.stTextInput input,
.stTextArea textarea {
    color: #F1F5F9 !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #8EA6C9 !important;
    opacity: 1 !important;
}

.question-header{
  margin-top:22px;
  padding:17px 20px 10px;

  border:1px solid #17345f;
  border-bottom:0;

  border-radius:18px 18px 0 0;

  background:
    linear-gradient(
      145deg,
      rgba(7,20,42,.96),
      rgba(3,11,25,.98)
    );
}

.question-title{
  font-weight:800;
  font-size:.92rem;
  color:#f4f7ff;
}

.question-status{
  float:right;
  color:#25df9a;
  font-size:.62rem;
  font-weight:600;
  margin-top:3px;
}

div[data-testid="stForm"]{
  width:100% !important;

  border:0 !important;
  background:transparent !important;

  padding:0 !important;
  margin:0 !important;
}

div[data-testid="stForm"] [data-testid="stHorizontalBlock"]{
  display:flex !important;
  flex-direction:row !important;
  flex-wrap:nowrap !important;

  align-items:center !important;

  gap:10px !important;

  width:100% !important;
}

div[data-testid="stForm"]
[data-testid="stHorizontalBlock"]
> div:first-child{

  flex:1 1 auto !important;

  width:auto !important;
  min-width:0 !important;
}

div[data-testid="stForm"]
div[data-testid="stTextInput"]{

  width:100% !important;

  margin:0 !important;
}

div[data-testid="stForm"]
div[data-testid="stTextInput"] > div{

  width:100% !important;
}

div[data-testid="stForm"]
div[data-testid="stTextInput"] input{

  width:100% !important;

  height:64px !important;
  min-height:64px !important;

  box-sizing:border-box !important;

  padding:0 20px !important;

  border:1px solid #24549a !important;

  border-radius:14px !important;

  background:
    linear-gradient(
      145deg,
      #07162e,
      #061227
    ) !important;

  color:#f7fbff !important;

  font-size:.92rem !important;

  font-family:"Inter",sans-serif !important;

  box-shadow:
    inset 0 1px 0 rgba(255,255,255,.02),
    0 8px 25px rgba(0,0,0,.12) !important;

  transition:all .18s ease !important;
}

div[data-testid="stForm"]
div[data-testid="stTextInput"]
input::placeholder{

  color:#7189ad !important;
}

div[data-testid="stForm"]
div[data-testid="stTextInput"]
input:focus{

  border-color:#4b83ff !important;

  box-shadow:
    0 0 0 1px rgba(75,131,255,.25),
    0 8px 30px rgba(43,127,255,.12) !important;
}

div[data-testid="stForm"]
[data-testid="stHorizontalBlock"]
> div:last-child{

  flex:0 0 50px !important;

  width:64px !important;
  min-width:64px !important;
}

div[data-testid="stForm"]
div[data-testid="stFormSubmitButton"]{

  width:64px !important;

  min-width:64px !important;

  margin:0 !important;

  padding:0 !important;
}

div[data-testid="stForm"]
div[data-testid="stFormSubmitButton"]
button{

  width:64px !important;

  min-width:64px !important;

  height:64px !important;

  min-height:64px !important;

  margin:0 !important;

  padding:0 !important;

  border-radius:14px !important;

  border:1px solid #4f8cff !important;

  background:
    linear-gradient(
      135deg,
      #176fff 0%,
      #713cff 100%
    ) !important;

  color:#ffffff !important;

  font-size:1.15rem !important;

  font-weight:800 !important;

  box-shadow:
    0 8px 25px rgba(43,104,255,.20) !important;

  transition:all .18s ease !important;
}

div[data-testid="stForm"]
div[data-testid="stFormSubmitButton"]
button:hover{

  transform:translateY(-1px) !important;

  border-color:#7ba7ff !important;

  box-shadow:
    0 12px 32px rgba(43,104,255,.32) !important;
}

div[data-testid="stForm"] > div{
  gap:8px !important;
}

.chat-panel + div{
  margin-top:16px !important;
}

.stButton>button{

  border-radius:10px!important;

  border:1px solid #204a84!important;

  font-weight:700!important;

  min-height:38px;

  background:#07162d!important;

  color:#edf4ff!important;
}

.stButton>button:hover{

  border-color:#3b7cda!important;

  background:#0a1d3a!important;
}

button[kind="primary"]{

  background:
    linear-gradient(
      90deg,
      #176fff,
      #7b3cff
    )!important;

  border-color:#4f8cff!important;

  box-shadow:
    0 7px 22px rgba(43,104,255,.18)!important;
}

.stTextInput input,
.stTextArea textarea,
[data-baseweb="select"]>div{

  border-radius:10px!important;

  background:#06152d!important;

  border-color:#1b4077!important;

  color:#f7fbff!important;
}

[data-testid="stFileUploader"]{

  background:rgba(4,14,30,.55)!important;

  border:1px dashed #27558f!important;

  border-radius:12px!important;

  padding:5px!important;
}

[data-testid="stFileUploaderDropzone"]{

  background:rgba(5,18,39,.72)!important;

  border:0!important;

  min-height:68px;
}

[data-testid="stFileUploaderDropzoneInstructions"]{

  font-size:.63rem!important;
}

[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"]{
  background:#07162e!important;
  border:1px solid #1b4077!important;
  border-radius:8px!important;
}

[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] *{
  color:#dce7f9!important;
}

[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"]:hover,
[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"]:hover *{
  background:#07162e!important;
  color:#dce7f9!important;
}

div[data-testid="stExpander"]{

  border-color:#193b6c!important;

  background:rgba(4,15,31,.6)!important;

  border-radius:10px!important;
}

div[data-testid="stExpander"] summary{

  font-size:.68rem!important;
}

.auth-spacer{
  height:34px;
}

[data-testid="stVerticalBlockBorderWrapper"]{

  border-color:#1d3f70!important;

  border-radius:20px!important;

  background:
    linear-gradient(
      145deg,
      rgba(8,21,44,.97),
      rgba(3,11,25,.98)
    )!important;

  box-shadow:
    0 24px 70px rgba(0,0,0,.42),
    0 0 55px rgba(54,77,255,.07)!important;

  padding:2px!important;
}

.auth-card{

  width:min(430px,100%);

  border:1px solid #1d3f70;

  border-radius:20px;

  background:
    linear-gradient(
      145deg,
      rgba(8,21,44,.97),
      rgba(3,11,25,.98)
    );

  box-shadow:
    0 24px 70px rgba(0,0,0,.42),
    0 0 55px rgba(54,77,255,.07);

  padding:27px 28px 23px;
}

.auth-logo{

  width:56px;
  height:56px;

  margin:0 auto 12px;

  border-radius:16px;

  display:flex;
  align-items:center;
  justify-content:center;

  font-size:25px;

  background:
    linear-gradient(
      135deg,
      #1978ff,
      #823cff
    );

  box-shadow:
    0 0 30px rgba(67,103,255,.28);
}

.auth-title{

  text-align:center;

  font-size:2rem;

  font-weight:800;

  letter-spacing:-.065em;
}

.auth-subtitle{

  text-align:center;

  font-size:.66rem;

  color:#829cc2;

  margin-top:6px;

  margin-bottom:20px;
}

.auth-heading{

  font-size:1rem;

  font-weight:800;

  margin-bottom:13px;
}

.auth-divider{

  display:flex;

  align-items:center;

  gap:10px;

  color:#637fa7;

  font-size:.59rem;

  margin:15px 0;
}

.auth-divider:before,
.auth-divider:after{

  content:"";

  height:1px;

  flex:1;

  background:#18345c;
}

.auth-foot{

  text-align:center;

  color:#5f7da5;

  font-size:.56rem;

  line-height:1.8;

  margin-top:16px;
}

.app-footer{

  text-align:center;

  color:#58749d;

  font-size:.56rem;

  line-height:1.8;

  padding:25px 8px 18px;

  margin-top:24px !important;

  margin-bottom:12px !important;

  position:relative !important;

  z-index:2 !important;
}

.app-footer b{
  color:#cbd8ff;
}

.app-footer a{

  color:#6fdcff;

  text-decoration:none;
}

.evidence-title{

  font-size:.68rem;

  font-weight:800;

  word-break:break-word;
}

.evidence-meta{

  font-size:.55rem;

  color:#6885aa;

  margin-top:3px;
}

.evidence-code{

  font:.57rem/1.5 ui-monospace,
  SFMono-Regular,
  Consolas,
  monospace;

  color:#c9d7ea;

  white-space:pre-wrap;

  overflow-wrap:anywhere;

  margin-top:8px;
}

@media(max-width:900px){

  .main-shell{

    width:calc(100% - 22px);
  }

  .workspace-head{

    align-items:flex-start;

    flex-direction:column;
  }

  .metrics{

    justify-content:flex-start;
  }

}

@media(max-width:650px){

  .main-shell{

    width:calc(100% - 12px);
  }

  .hero{

    padding:20px 5px 16px;
  }

  .hero-title{

    font-size:2.35rem!important;
  }

  .hero-sub{

    font-size:.72rem;
  }

  .upload-panel{

    padding:16px 12px 12px;
  }

  [data-testid="stAppViewContainer"]
  .main
  .block-container{

    padding:22px 16px 42px;
  }

  .mode-strip{

    grid-template-columns:repeat(2,1fr);

    gap:10px;
  }

  .auth-spacer{

    height:12px;
  }

  [data-testid="stVerticalBlockBorderWrapper"]{

    border-radius:17px!important;
  }

  div[data-testid="stForm"]
  [data-testid="stHorizontalBlock"]{

    display:flex !important;

    flex-direction:row !important;

    flex-wrap:nowrap !important;

    align-items:center !important;

    gap:7px !important;

    width:100% !important;
  }

  div[data-testid="stForm"]
  [data-testid="stHorizontalBlock"]
  > div:first-child{

    flex:1 1 auto !important;

    width:auto !important;

    min-width:0 !important;
  }

  div[data-testid="stForm"]
  [data-testid="stHorizontalBlock"]
  > div:last-child{

    flex:0 0 58px !important;

    width:58px !important;

    min-width:58px !important;
  }

  div[data-testid="stForm"]
  div[data-testid="stTextInput"]
  input{

    width:100% !important;

    height:58px !important;

    min-height:58px !important;

    padding:0 14px !important;

    font-size:.80rem !important;

    box-sizing:border-box !important;
  }

  div[data-testid="stForm"]
  div[data-testid="stFormSubmitButton"]{

    width:58px !important;

    min-width:58px !important;

    margin:0 !important;

    padding:0 !important;
  }

  div[data-testid="stForm"]
  div[data-testid="stFormSubmitButton"]
  button{

    width:58px !important;

    min-width:58px !important;

    height:58px !important;

    min-height:58px !important;

    margin:0 !important;

    padding:0 !important;

    border-radius:13px !important;

    font-size:1rem !important;
  }

  .question-header{

    margin-top:16px;

    padding:14px 15px 9px;
  }

  .question-title{

    font-size:.85rem;
  }

  .question-status{

    font-size:.55rem;
  }

  .app-footer{

    margin-top:22px !important;

    padding:20px 8px 15px !important;
  }

}

@media(max-width:420px){

  [data-testid="stAppViewContainer"]
  .main
  .block-container{

    padding-left:10px !important;

    padding-right:10px !important;
  }

  .hero-title{

    font-size:2rem!important;
  }

  .mode-strip{

    grid-template-columns:1fr 1fr;

    gap:8px;
  }

  .mode-card{

    padding:11px 10px;
  }

  .mode-name{

    font-size:.58rem;
  }

  .mode-text{

    font-size:.48rem;
  }

  div[data-testid="stForm"]
  [data-testid="stHorizontalBlock"]{

    gap:6px !important;
  }

  div[data-testid="stForm"]
  [data-testid="stHorizontalBlock"]
  > div:last-child{

    flex:0 0 54px !important;

    width:54px !important;

    min-width:54px !important;
  }

  div[data-testid="stForm"]
  div[data-testid="stFormSubmitButton"]{

    width:54px !important;

    min-width:54px !important;
  }

  div[data-testid="stForm"]
  div[data-testid="stFormSubmitButton"]
  button{

    width:54px !important;

    min-width:54px !important;

    height:54px !important;

    min-height:54px !important;

    border-radius:12px !important;
  }

  div[data-testid="stForm"]
  div[data-testid="stTextInput"]
  input{

    height:54px !important;

    min-height:54px !important;

    padding:0 12px !important;

    font-size:.76rem !important;
  }

}

@media(max-width:650px){

  div[data-testid="stForm"]
  [data-testid="stHorizontalBlock"]
  > [data-testid="column"]{

    width:auto !important;

    min-width:0 !important;
  }

}

@media(max-width:650px){

    div[data-testid="stForm"]
    div[data-testid="stFormSubmitButton"]
    button{

      height:54px !important;
      min-height:54px !important;

        width:58px !important;
        min-width:58px !important;

        border-radius:13px !important;
    }

}

div[data-testid="stForm"] input[type="text"]{
  height:58px !important;
  min-height:58px !important;
  box-sizing:border-box !important;
}

div[data-testid="stForm"] button[type="submit"]{
  height:58px !important;
  min-height:58px !important;
  box-sizing:border-box !important;
}

div[data-testid="stForm"] div[data-baseweb="input"],
div[data-testid="stForm"] div[data-baseweb="input"] > div,
div[data-testid="stForm"] div[data-baseweb="input"] input{
  height:58px !important;
  min-height:58px !important;
  box-sizing:border-box !important;
}

input[placeholder*="Ask anything about your indexed repository"]{
  height:36px !important;
  min-height:36px !important;
  box-sizing:border-box !important;
}

div[data-baseweb="input"]:has(input[placeholder*="Ask anything about your indexed repository"]),
div[data-baseweb="input"]:has(input[placeholder*="Ask anything about your indexed repository"]) > div{
  height:36px !important;
  min-height:36px !important;
  box-sizing:border-box !important;
}

div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] button{
  height:36px !important;
  min-height:36px !important;
  border-radius:8px !important;
}

div[data-baseweb="select"] > div {
    background: #07152b !important;
    border: 1px solid #244b7a !important;
    color: #f4f7ff !important;
    border-radius: 10px !important;
}

div[data-baseweb="select"] span {
    color: #f4f7ff !important;
}

div[data-baseweb="select"] svg {
    fill: #cbd5e1 !important;
}

section[data-testid="stFileUploaderDropzone"] {
    background: #07152b !important;
    border: 1px dashed #24558c !important;
    border-radius: 12px !important;
}

section[data-testid="stFileUploaderDropzone"] * {
    color: #dbeafe !important;
}

section[data-testid="stFileUploaderDropzone"] button {
    background: #172554 !important;
    color: #ffffff !important;
    border: 1px solid #315ca8 !important;
    border-radius: 9px !important;
}

section[data-testid="stFileUploaderDropzone"] button:hover {
    background: #243b78 !important;
    color: #ffffff !important;
}

div[data-baseweb="popover"] {
    background: #07152b !important;
}

div[data-baseweb="menu"] {
    background: #07152b !important;
}

div[data-baseweb="menu"] li {
    background: #07152b !important;
    color: #f4f7ff !important;
}

div[data-baseweb="menu"] li:hover {
    background: #132a4a !important;
    color: #ffffff !important;
}

[data-testid="stSidebar"] {
    color: #e8eefc !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] div,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] small {
    color: #dbe7ff !important;
    opacity: 1 !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
[data-testid="stSidebar"] h5,
[data-testid="stSidebar"] h6,
[data-testid="stSidebar"] label {
    color: #f4f7ff !important;
    opacity: 1 !important;
}

[data-testid="stSidebar"] button {
    color: #eaf2ff !important;
}

[data-testid="stSidebar"] button p,
[data-testid="stSidebar"] button span {
    color: #eaf2ff !important;
    opacity: 1 !important;
}

[data-testid="stSidebar"] .caption,
[data-testid="stSidebar"] small {
    color: #9fb4d4 !important;
    opacity: 1 !important;
}

[data-testid="stSidebar"] div[data-baseweb="select"] span {
    color: #f4f7ff !important;
    opacity: 1 !important;
}

[data-testid="stSidebar"] * {
    text-shadow: none;
}

</style>
""",
    unsafe_allow_html=True,
)

SUPPORTED = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".c", ".cpp", ".h",
    ".hpp", ".cs", ".go", ".rs", ".php", ".rb", ".swift", ".kt", ".kts",
    ".sql", ".html", ".css", ".json", ".yaml", ".yml", ".md", ".txt",
    ".xml", ".sh", ".bat", ".dockerfile"
}

IGNORED_DIRS = {
    ".git", ".github", ".idea", ".vscode", "__pycache__", "node_modules",
    "venv", ".venv", "env", ".env", "dist", "build", ".next", "coverage",
    ".pytest_cache", ".mypy_cache"
}

MODEL_OPTIONS = [
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-20b",
    "openai/gpt-oss-7b",
]

DB_PATH = Path("data") / "repomind_users.db"
DB_PATH.parent.mkdir(exist_ok=True)

def db():
    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            messages TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    user_columns = {
        row[1] for row in conn.execute("PRAGMA table_info(users)").fetchall()
    }

    if "full_name" not in user_columns:
        conn.execute("ALTER TABLE users ADD COLUMN full_name TEXT DEFAULT 'User'")

    if "email" not in user_columns:
        conn.execute("ALTER TABLE users ADD COLUMN email TEXT DEFAULT ''")

    chat_columns = {
        row[1] for row in conn.execute("PRAGMA table_info(chats)").fetchall()
    }

    if "updated_at" not in chat_columns:
        conn.execute("ALTER TABLE chats ADD COLUMN updated_at TEXT")

    conn.execute(
        "UPDATE chats SET updated_at = created_at WHERE updated_at IS NULL"
    )

    conn.commit()
    return conn

def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120_000,
    ).hex()

    return digest, salt

def valid_email(email):
    return re.match(
        r"^[^@\s]+@gmail\.com$",
        email.strip().lower()
    ) is not None

def create_user(full_name, email, password):
    full_name = full_name.strip()
    email = email.strip().lower()

    if len(full_name) < 2:
        return False, "Enter your full name."

    if not valid_email(email):
        return False, "Please use a valid Gmail address."

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    conn = db()

    try:
        digest, salt = hash_password(password)

        conn.execute(
            """
            INSERT INTO users(full_name,email,password_hash,salt)
            VALUES(?,?,?,?)
            """,
            (full_name, email, digest, salt),
        )

        conn.commit()

        return True, "Account created successfully."

    except sqlite3.IntegrityError:
        return False, "This Gmail is already registered."

    finally:
        conn.close()

def authenticate(email, password):
    email = email.strip().lower()

    conn = db()

    row = conn.execute(
        """
        SELECT id,full_name,email,password_hash,salt
        FROM users
        WHERE email=?
        """,
        (email,),
    ).fetchone()

    conn.close()

    if not row:
        return None

    digest, _ = hash_password(password, row[4])

    if secrets.compare_digest(digest, row[3]):
        return {
            "id": row[0],
            "full_name": row[1],
            "email": row[2],
        }

    return None

def load_chats(user_id):
    conn = db()

    rows = conn.execute(
        """
        SELECT id,title,messages
        FROM chats
        WHERE user_id=?
        ORDER BY COALESCE(updated_at, created_at) DESC, id DESC
        """,
        (user_id,),
    ).fetchall()

    conn.close()

    result = []

    for row in rows:
        try:
            messages = json.loads(row[2])
        except Exception:
            messages = []

        result.append({
            "id": row[0],
            "title": row[1],
            "messages": messages,
        })

    return result

def save_chat(user_id, chat_id, title, messages):
    conn = db()

    payload = json.dumps(
        messages,
        ensure_ascii=False
    )

    if chat_id is None:
        cur = conn.execute(
            """
            INSERT INTO chats(user_id,title,messages,updated_at)
            VALUES(?,?,?,CURRENT_TIMESTAMP)
            """,
            (user_id, title, payload),
        )

        chat_id = cur.lastrowid

    else:
        conn.execute(
            """
            UPDATE chats
            SET title=?, messages=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=? AND user_id=?
            """,
            (title, payload, chat_id, user_id),
        )

    conn.commit()
    conn.close()

    return chat_id

def delete_chat(user_id, chat_id):
    conn = db()

    conn.execute(
        "DELETE FROM chats WHERE id=? AND user_id=?",
        (chat_id, user_id),
    )

    conn.commit()
    conn.close()

@st.cache_resource(show_spinner=False)
def load_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

def safe_decode(data: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue

    return ""

def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()

def extract_pdf(uploaded_file):
    reader = PdfReader(
        io.BytesIO(uploaded_file.getvalue())
    )

    records = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if text.strip():
            records.append({
                "source": uploaded_file.name,
                "path": uploaded_file.name,
                "page": page_number,
                "text": normalize_text(text),
                "type": "pdf",
            })

    return records

def extract_zip(uploaded_file):
    records = []

    with zipfile.ZipFile(
        io.BytesIO(uploaded_file.getvalue())
    ) as archive:

        for info in archive.infolist():

            if info.is_dir():
                continue

            parts = Path(info.filename).parts

            if any(
                part.lower() in IGNORED_DIRS
                for part in parts[:-1]
            ):
                continue

            extension = Path(info.filename).suffix.lower()
            filename = Path(info.filename).name.lower()

            if (
                extension not in SUPPORTED
                and filename != "dockerfile"
            ):
                continue

            try:
                raw = archive.read(info)
                text = safe_decode(raw)

                if not text.strip():
                    continue

                records.append({
                    "source": uploaded_file.name,
                    "path": info.filename,
                    "page": None,
                    "text": normalize_text(text),
                    "type": "code",
                })

            except Exception:
                continue

    return records

def extract_single_code(uploaded_file):
    text = safe_decode(
        uploaded_file.getvalue()
    )

    if not text.strip():
        return []

    return [{
        "source": uploaded_file.name,
        "path": uploaded_file.name,
        "page": None,
        "text": normalize_text(text),
        "type": "code",
    }]

def chunk_text(record, chunk_size=1200, overlap=180):
    text = record["text"]

    if len(text) <= chunk_size:
        return [{
            **record,
            "chunk": text,
            "chunk_id": 0,
        }]

    chunks = []
    start = 0
    chunk_id = 0

    while start < len(text):

        end = min(
            start + chunk_size,
            len(text)
        )

        chunks.append({
            **record,
            "chunk": text[start:end],
            "chunk_id": chunk_id,
        })

        if end >= len(text):
            break

        start = max(
            end - overlap,
            start + 1
        )

        chunk_id += 1

    return chunks

def build_index(chunks, model):
    texts = [
        chunk["chunk"]
        for chunk in chunks
    ]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
        batch_size=32,
    )

    embeddings = np.asarray(
        embeddings,
        dtype=np.float32
    )

    index = faiss.IndexFlatIP(
        embeddings.shape[1]
    )

    index.add(embeddings)

    return index

def retrieve(
    query,
    chunks,
    vector_index,
    model,
    top_k=6,
    similarity_threshold=0.22,
):
    query_embedding = model.encode(
        [query],
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    query_embedding = np.asarray(
        query_embedding,
        dtype=np.float32
    )

    search_k = min(
        top_k,
        len(chunks)
    )

    scores, indices = vector_index.search(
        query_embedding,
        search_k,
    )

    results = []

    for score, index in zip(
        scores[0],
        indices[0]
    ):
        if index < 0:
            continue

        score = float(score)

        if score < similarity_threshold:
            continue

        item = dict(
            chunks[int(index)]
        )

        item["score"] = score

        results.append(item)

    return results

def call_llm(
    api_key,
    model_name,
    question,
    results,
    mode,
):
    client = Groq(api_key=api_key)

    context_blocks = []

    for number, result in enumerate(
        results,
        start=1
    ):

        location = result["path"]

        if result.get("page"):
            location += (
                f" (page {result['page']})"
            )

        context_blocks.append(
            f"[SOURCE {number}] "
            f"{location}\n"
            f"{result['chunk']}"
        )

    context = "\n\n".join(
        context_blocks
    )

    instructions = {
        "Ask Repository":
            "Answer directly using only retrieved repository context.",

        "Explain Code":
            "Explain the relevant implementation, files, functions, "
            "classes, data flow and important logic. Do not invent details.",

       "Architecture":
           "Answer only the exact architecture question asked. "
            "List only components explicitly named in the retrieved context. "
            "Explain an interaction only if that interaction is explicitly described "
            "in the retrieved context. "
           "Do not infer a workflow or causal relationship from   component names alone. "
           "Do not include limitations, future improvements, future vision, project goals, "
           "author information, or unrelated sections unless explicitly requested. "
           "Do not add any information that is not directly supported by the retrieved context.",

        "Debug / Diagnose":
            "Diagnose the likely issue using retrieved code. "
            "Point to relevant files/functions and suggest a concrete fix. "
            "Clearly label uncertainty.",
    }

    prompt = f"""
You are RepoMind AI, a precise codebase intelligence assistant
powered by Retrieval-Augmented Generation.

RULES:
- Use ONLY the retrieved context.
- Never fabricate files, functions, classes, APIs, dependencies or behavior.
- If evidence is insufficient, say:
  "I couldn't find enough evidence in the indexed repository."
- Mention exact file paths and function/class names when possible.
- Keep the answer practical and developer-friendly.

TASK MODE:
{mode}

TASK INSTRUCTION:
{instructions[mode]}

DEVELOPER QUESTION:
{question}

RETRIEVED CONTEXT:
{context}
"""

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content":
                    "You are a precise, grounded software engineering assistant.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.15,
        max_tokens=1000,
    )

    return response.choices[0].message.content

defaults = {
    "authenticated": False,
    "user": None,
    "auth_view": "login",
    "chats": [],
    "current_chat_id": None,
    "messages": [],
    "chunks": [],
    "vector_index": None,
    "indexed_files": [],
    "last_results": [],
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

def render_footer():
    st.markdown(
        """
        <div class="app-footer">
            Built with RAG · Sentence Transformers · Groq · Streamlit
            <br>
            Created by <b>Subham Das</b>
            · AI/ML Engineer | Data Scientist | Data Analyst
            <br>
            <a href="https://github.com/DasSubham-2005" target="_blank">
                GitHub
            </a>
            &nbsp;·&nbsp;
            <a href="https://www.linkedin.com/in/subham-das-a316422b/" target="_blank">
                LinkedIn
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

if not st.session_state.authenticated:

    st.markdown(
        '<div class="auth-spacer"></div>',
        unsafe_allow_html=True
    )

    left, center, right = st.columns(
        [1.15, 1.0, 1.15]
    )

    with center:

        with st.container(border=True):

            st.markdown(
                """
                <div class="auth-logo">🧠</div>
                <div class="auth-title">RepoMind AI</div>
                <div class="auth-subtitle">Private codebase intelligence workspace</div>
                """,
                unsafe_allow_html=True,
            )

            if st.session_state.auth_view == "login":

                st.markdown(
                    '<div class="auth-heading">Welcome back</div>',
                    unsafe_allow_html=True
                )

                email = st.text_input(
                    "Gmail",
                    placeholder="you@gmail.com",
                    key="login_email",
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    key="login_password",
                )

                if st.button(
                    "Enter RepoMind",
                    type="primary",
                    use_container_width=True
                ):

                    if not email or not password:

                        st.warning(
                            "Enter your Gmail and password."
                        )

                    else:

                        user = authenticate(
                            email,
                            password
                        )

                        if user:

                            st.session_state.authenticated = True
                            st.session_state.user = user
                            st.session_state.chats = load_chats(
                                user["id"]
                            )
                            st.session_state.messages = []
                            st.session_state.current_chat_id = None
                            st.session_state.chunks = []
                            st.session_state.vector_index = None
                            st.session_state.indexed_files = []
                            st.session_state.last_results = []

                            st.rerun()

                        else:

                            st.error(
                                "Invalid Gmail or password."
                            )

                st.markdown(
                    '<div class="auth-divider">or</div>',
                    unsafe_allow_html=True
                )

                if st.button(
                    "Create a new account",
                    use_container_width=True
                ):

                    st.session_state.auth_view = "register"
                    st.rerun()

            else:

                st.markdown(
                    '<div class="auth-heading">Create your account</div>',
                    unsafe_allow_html=True
                )

                full_name = st.text_input(
                    "Full name",
                    placeholder=" your name",
                    key="register_name",
                )

                email = st.text_input(
                    "Gmail",
                    placeholder="you@gmail.com",
                    key="register_email",
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    key="register_password",
                )

                confirm = st.text_input(
                    "Confirm password",
                    type="password",
                    key="register_confirm",
                )

                if st.button(
                    "Create account",
                    type="primary",
                    use_container_width=True
                ):

                    if password != confirm:

                        st.error(
                            "Passwords do not match."
                        )

                    else:

                        ok, message = create_user(
                            full_name,
                            email,
                            password
                        )

                        if ok:

                            st.session_state.auth_view = "login"
                            st.session_state.login_email = email

                            st.rerun()

                        else:

                            st.error(message)

                st.markdown(
                    '<div class="auth-divider">or</div>',
                    unsafe_allow_html=True
                )

                if st.button(
                    "← Back to login",
                    use_container_width=True
                ):

                    st.session_state.auth_view = "login"
                    st.rerun()

            st.markdown(
                """
                <div class="auth-foot">
                    🔒 Your account keeps chat history private and isolated.
                </div>
                """,
                unsafe_allow_html=True,
            )

    render_footer()
    st.stop()

api_key = os.getenv(
    "GROQ_API_KEY",
    ""
)

user = st.session_state.user

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-title">
                <span class="sidebar-dot"></span>
                RepoMind AI
            </div>
            <div class="sidebar-sub">
                Codebase Intelligence Workspace
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    safe_name = html.escape(
        user["full_name"]
    )

    safe_email = html.escape(
        user["email"]
    )

    st.markdown(
        f"""
        <div class="user-card">
            <div class="user-name">👤 {safe_name}</div>
            <div class="user-email">{safe_email}</div>
            <div class="user-note">
                Private workspace · Your history only
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "＋ New Chat",
        use_container_width=True,
    ):

        st.session_state.current_chat_id = None
        st.session_state.messages = []
        st.session_state.last_results = []

        st.rerun()

    st.markdown(
        "##### 💬 Your chats"
    )

    if st.session_state.chats:

        for chat in st.session_state.chats[:15]:

            title = chat["title"].strip()

            if len(title) > 30:
                title = title[:30] + "…"

            col1, col2 = st.columns(
                [5, 1]
            )

            with col1:

                if st.button(
                    title or "New conversation",
                    key=f"chat_{chat['id']}",
                    use_container_width=True,
                ):

                    st.session_state.current_chat_id = chat["id"]
                    st.session_state.messages = chat["messages"]
                    st.session_state.last_results = []

                    st.rerun()

            with col2:

                if st.button(
                    "×",
                    key=f"delete_{chat['id']}",
                ):

                    delete_chat(
                        user["id"],
                        chat["id"],
                    )

                    st.session_state.chats = load_chats(
                        user["id"]
                    )

                    if (
                        st.session_state.current_chat_id
                        == chat["id"]
                    ):

                        st.session_state.current_chat_id = None
                        st.session_state.messages = []

                    st.rerun()

    else:

        st.caption(
            "No conversations yet."
        )

    st.divider()

    st.markdown(
        "##### 🎛️ Analysis"
    )

    mode = st.selectbox(
        "Analysis mode",
        [
            "Ask Repository",
            "Explain Code",
            "Architecture",
            "Debug / Diagnose",
        ],
        label_visibility="collapsed",
    )

    model_name = st.selectbox(
        "LLM model",
        MODEL_OPTIONS,
        index=0,
        label_visibility="collapsed",
    )

    with st.expander(
        "⚙️ Retrieval settings"
    ):

        top_k = st.slider(
            "Retrieved chunks",
            3,
            10,
            6,
        )

        chunk_size = st.slider(
            "Chunk size",
            700,
            1800,
            1200,
            100,
        )

        overlap = st.slider(
            "Chunk overlap",
            50,
            300,
            180,
            10,
        )

    st.divider()

    if api_key:

        st.success(
            "Groq API configured"
        )

    else:

        st.warning(
            "GROQ_API_KEY not found"
        )

    st.caption(
        "🔒 Chat history is isolated by account."
    )

    st.caption(
        "📦 Repository index stays in the active session."
    )

    if st.button(
        "🚪 Logout",
        use_container_width=True,
    ):

        for key, value in defaults.items():
            st.session_state[key] = value

        st.rerun()

st.markdown(
    """
    <div class="hero">
            <div class="hero-kicker">RAG · SEMANTIC SEARCH · GROQ</div>
            <div class="hero-title">RepoMind AI</div>
            <div class="hero-sub">AI-powered codebase intelligence for your repository</div>
            <div class="hero-pills">
                <div class="hero-pill">✦ RAG-Powered</div>
                <div class="hero-pill">⌕ Semantic Search</div>
                <div class="hero-pill">◈ Groq</div>
            </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="panel upload-panel">
      <div class="panel-head">
        <div class="panel-icon">☁</div>
        <div>
          <div class="panel-title">Upload your codebase</div>
          <div class="panel-sub">GitHub ZIP, source files or PDF documentation</div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

uploads = st.file_uploader(
    "Browse files",
    type=[
        "zip", "py", "js", "jsx", "ts", "tsx",
        "java", "cpp", "c", "h", "cs", "go", "rs",
        "php", "rb", "swift", "kt", "sql", "html",
        "css", "json", "yaml", "yml", "md", "txt", "pdf",
    ],
    accept_multiple_files=True,
    label_visibility="collapsed",
    help="Upload a GitHub repository ZIP for the best experience.",
)

st.markdown(
    """
        <div style="font-size:.54rem;color:#607da4;margin-top:8px;letter-spacing:.03em;">
            ZIP · PY · JS · TS · JAVA · C/C++ · PDF · MD · JSON · YAML
        </div>
    """,
    unsafe_allow_html=True,
)

if uploads:

    if st.button(
        "🚀 Build RAG Index",
        type="primary",
        use_container_width=True
    ):

        with st.spinner(
            "Reading files → chunking → generating embeddings..."
        ):

            records = []

            for file in uploads:

                extension = Path(
                    file.name
                ).suffix.lower()

                if extension == ".zip":

                    records.extend(
                        extract_zip(file)
                    )

                elif extension == ".pdf":

                    records.extend(
                        extract_pdf(file)
                    )

                else:

                    records.extend(
                        extract_single_code(file)
                    )

            chunks = []

            for record in records:

                chunks.extend(
                    chunk_text(
                        record,
                        chunk_size,
                        overlap
                    )
                )

            if not chunks:

                st.error(
                    "No supported readable files were found."
                )

            else:

                model = load_embedding_model()

                vector_index = build_index(
                    chunks,
                    model
                )

                st.session_state.chunks = chunks

                st.session_state.vector_index = vector_index

                st.session_state.indexed_files = sorted(
                    set(
                        record["path"]
                        for record in records
                    )
                )

                st.session_state.last_results = []

                st.rerun()

st.markdown(
    '<div class="section-row"><div class="section-title">Repository workspace</div>'
    '<div class="section-note">Your active session</div></div>',
    unsafe_allow_html=True,
)

if st.session_state.chunks:

    files_count = len(
        st.session_state.indexed_files
    )

    chunks_count = len(
        st.session_state.chunks
    )

    st.markdown(
        f"""
        <div class="workspace">
            <div class="workspace-head">
                <div>
                    <div class="workspace-name">📦 Repository indexed</div>
                    <div class="workspace-note">Your codebase is ready for grounded questions.</div>
                </div>
                <div class="metrics">
                    <div class="metric"><div class="metric-label">FILES</div><div class="metric-value">{files_count}</div></div>
                    <div class="metric"><div class="metric-label">CHUNKS</div><div class="metric-value">{chunks_count}</div></div>
                    <div class="metric"><div class="metric-label">STATUS</div><div class="metric-value ready">✓ READY</div></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

else:

    st.markdown(
        """
        <div class="workspace">
            <div class="workspace-name">📦 No repository indexed</div>
            <div class="workspace-note">Upload your codebase above and build the RAG index to begin.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="section-row"><div class="section-title">What RepoMind can do</div></div>',
    unsafe_allow_html=True,
)

capabilities = [
    ("🧠", "RAG", "Grounded answers"),
    ("🔎", "Search", "Semantic retrieval"),
    ("💻", "Code", "Explain & debug"),
    ("🏗️", "Architecture", "Trace components"),
]

cards_html = '<div class="mode-strip">' + ''.join(
    f'<div class="mode-card"><div class="mode-icon">{icon}</div>'
    f'<div class="mode-name">{name}</div><div class="mode-text">{description}</div></div>'
    for icon, name, description in capabilities
) + '</div>'

st.markdown(
    cards_html,
    unsafe_allow_html=True
)

if st.session_state.chunks:

    st.markdown(
       """
       <div class="question-header">
          <div class="question-title">💬 Ask RepoMind</div>
          <div class="question-status">● Grounded by repository evidence</div>
       </div>
       """,
      unsafe_allow_html=True,
    )

    if st.session_state.messages:
       for message in st.session_state.messages:
          with st.chat_message(message["role"]):
             st.markdown(message["content"])

    with st.form(
        "repo_question_form",
        clear_on_submit=True
    ):

        question_col, button_col = st.columns(
            [8, 1]
        )

        with question_col:

            question = st.text_input(
                "Question",
                placeholder="Ask anything about your indexed repository…",
                label_visibility="collapsed",
            )

        with button_col:

            submit = st.form_submit_button(
                "➤",
                use_container_width=True,
            )

    if submit and question.strip():

        question = question.strip()

        model = load_embedding_model()

        results = retrieve(
            question,
            st.session_state.chunks,
            st.session_state.vector_index,
            model,
            top_k,
            similarity_threshold=0.22,
        )

        st.session_state.last_results = results

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        answer = ""

        if not results:

            answer = (
                "I couldn't find enough evidence "
                "in the indexed repository."
            )

        elif not api_key:

            answer = (
                "I can retrieve semantic evidence, "
                "but a Groq API key is not configured."
            )

        else:

            with st.spinner(
                "Analyzing repository evidence..."
            ):

                try:
                    

                    answer = call_llm(
                        api_key,
                        model_name,
                        question,
                        results,
                        mode
                    )
                    if answer is None:
                        answer = ""

                    answer = str(answer).strip()

                    if not answer:
                        answer = "I couldn't find enough evidence in the indexed repository."

                except Exception as error:

                    answer = f"LLM error: {error}"
                    

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

        title = (
            question.replace("\n", " ")[:55]
            or "New conversation"
        )

        new_id = save_chat(
            user["id"],
            st.session_state.current_chat_id,
            title,
            st.session_state.messages
        )

        st.session_state.current_chat_id = new_id

        st.session_state.chats = load_chats(
            user["id"]
        )

        st.rerun()

    st.markdown(
        "<div style='height:4px'></div>",
        unsafe_allow_html=True
    )



if st.session_state.last_results:

    with st.expander(
        "📚 View Evidence",
        expanded=False
    ):

        st.markdown(
            '<div class="section-row"><div class="section-title">Retrieved evidence</div>'
            '<div class="section-note">Top semantic matches</div></div>',
            unsafe_allow_html=True,
        )

        for number, result in enumerate(
            st.session_state.last_results,
            start=1
        ):

            location = result["path"]

            if result.get("page"):
                location += (
                    f" · Page {result['page']}"
                )

            preview = result["chunk"][:900]

            if len(result["chunk"]) > 900:
                preview += "..."

            safe_location = html.escape(
                location
            )

            safe_preview = html.escape(
                preview
            )

            with st.container(
                border=True
            ):
                st.markdown(
                    f"""
                    <div class="evidence-title">{number}. {safe_location}</div>
                    <div class="evidence-meta">Semantic relevance · {result["score"]:.3f}</div>
                    <div class="evidence-code">{safe_preview}</div>
                    """,
                    unsafe_allow_html=True,
                )

if st.session_state.indexed_files:

    with st.expander(
        "📂 View indexed files"
    ):

        for filename in st.session_state.indexed_files:

            st.write(
                f"• {filename}"
            )

render_footer()