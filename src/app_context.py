import streamlit as st

from src.repository_supabase import SupabaseRepository


@st.cache_resource
def repository() -> SupabaseRepository:
    return SupabaseRepository()
