from langchain_community.llms import Ollama
from langchain_core.output_parsers import JsonOutputParser
import sqlite3
import json
from pathlib import Path
import streamlit as st

class SpecAgent:
    def __init__(self):
        self.llm = Ollama(model="llama3:8b", temperature=0.2)
        self.parser = JsonOutputParser()

    def process_rfq(self, text):
        prompt = f"""Extract key information from the RFQ:
        {{
            "material": "chemical name",
            "purity": "percentage",
            "quantity": "kg/month",
            "technical_requirements": "list of requirements"
        }}
        Input: {text}"""
        return self.parser.parse(self.llm(prompt))

class MatchmakerAgent:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY,
                name TEXT,
                chemical TEXT,
                purity REAL,
                delivery_rating REAL,
                min_order REAL
            )
        """)
        conn.commit()
        conn.close()

    def add_supplier(self, supplier_data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO suppliers (name, chemical, purity, delivery_rating, min_order)
            VALUES (?, ?, ?, ?, ?)
        """, (
            supplier_data['name'],
            supplier_data['chemical'],
            supplier_data['purity'],
            supplier_data['delivery_rating'],
            supplier_data['min_order']
        ))
        conn.commit()
        conn.close()

    def find_suppliers(self, specs):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, chemical, purity, delivery_rating, min_order,
            (1 - ABS(purity - ?)) * 0.6 + 
            (delivery_rating) * 0.4 AS score
            FROM suppliers
            WHERE chemical = ?
            ORDER BY score DESC
        """, (specs['purity'], specs['material']))
        results = cursor.fetchall()
        conn.close()
        return [{
            'name': row[0],
            'chemical': row[1],
            'purity': row[2],
            'delivery_rating': row[3],
            'min_order': row[4],
            'score': row[5]
        } for row in results]

def main():
    st.title("Raw Material Development Assistant")
    
    # Initialize agents
    spec_agent = SpecAgent()
    matchmaker = MatchmakerAgent("suppliers.db")
    
    # Create inputs folder if it doesn't exist
    inputs_dir = Path("inputs")
    inputs_dir.mkdir(exist_ok=True)
    
    # Sidebar for supplier management
    with st.sidebar:
        st.header("Supplier Management")
        if st.button("Add New Supplier"):
            with st.form("new_supplier"):
                supplier_name = st.text_input("Supplier Name")
                chemical = st.text_input("Material")
                purity = st.number_input("Purity (0-100)", min_value=0.0, max_value=100.0)
                delivery_rating = st.number_input("Delivery Rating (0-10)", min_value=0.0, max_value=10.0)
                min_order = st.number_input("Minimum Order (kg)", min_value=0.0)
                
                if st.form_submit_button("Add Supplier"):
                    matchmaker.add_supplier({
                        'name': supplier_name,
                        'chemical': chemical,
                        'purity': purity,
                        'delivery_rating': delivery_rating,
                        'min_order': min_order
                    })
                    st.success("Supplier added successfully!")
    
    # Main content
    st.header("Process RFQ")
    rfq_text = st.text_area("Paste RFQ text here:")
    
    if st.button("Process RFQ"):
        if rfq_text:
            with st.spinner("Analyzing RFQ..."):
                try:
                    specs = spec_agent.process_rfq(rfq_text)
                    st.json(specs)
                    
                    with st.spinner("Finding suitable suppliers..."):
                        suppliers = matchmaker.find_suppliers(specs)
                        st.subheader("Recommended Suppliers")
                        for supplier in suppliers:
                            st.write(f"**{supplier['name']}**")
                            st.write(f"- Purity Match: {supplier['purity']}%")
                            st.write(f"- Delivery Rating: {supplier['delivery_rating']}/10")
                            st.write(f"- Minimum Order: {supplier['min_order']} kg")
                            st.write(f"- Score: {supplier['score']:.2f}")
                            st.write("---")
                except Exception as e:
                    st.error(f"Error processing RFQ: {str(e)}")
        else:
            st.warning("Please enter RFQ text")

if __name__ == "__main__":
    main()
