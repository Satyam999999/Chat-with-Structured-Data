import streamlit as st
import pandas as pd
from nl2sql import ask_database
import os

st.set_page_config(page_title="Chat with Data", page_icon="📊", layout="wide")

st.title("📊 Chat with Structured Data")
st.markdown("Ask natural language questions about the retail database (Customers, Products, Orders).")

# Sidebar for API Key if not set in env
if not os.environ.get("GROQ_API_KEY"):
    api_key = st.sidebar.text_input("Enter Groq API Key:", type="password")
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key
    else:
        st.warning("Please enter your Groq API Key in the sidebar to continue.")
        st.stop()

# Chat interface
question = st.text_input("Ask a question:", placeholder="e.g. What were the total sales by product category?")

if st.button("Generate & Run SQL") or question:
    if question:
        with st.spinner("Generating SQL query..."):
            sql, df, error = ask_database(question)
            
            if error:
                st.error(f"Error: {error}")
            else:
                st.success("Query executed successfully!")
                
                # Show SQL
                with st.expander("View Generated SQL", expanded=True):
                    st.code(sql, language="sql")
                    
                # Show Data
                st.subheader("Results")
                st.dataframe(df, use_container_width=True)
                
                # Simple Chart heuristic
                if not df.empty and len(df.columns) >= 2:
                    # Look for one numeric and one categorical
                    numeric_cols = df.select_dtypes(include='number').columns.tolist()
                    cat_cols = df.select_dtypes(exclude='number').columns.tolist()
                    
                    if len(numeric_cols) >= 1 and len(cat_cols) >= 1:
                        st.subheader("Visualization")
                        # Try to use the first categorical as X and first numeric as Y
                        chart_data = df.set_index(cat_cols[0])
                        st.bar_chart(chart_data[numeric_cols[0]])
                    elif len(numeric_cols) >= 2:
                        st.subheader("Visualization")
                        chart_data = df.set_index(numeric_cols[0])
                        st.line_chart(chart_data[numeric_cols[1]])
    else:
        st.warning("Please enter a question.")
