import streamlit as st
from supply_ai.agents.spec_agent import SpecAgent
from supply_ai.agents.matchmaker_agent import MatchmakerAgent
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize agents
spec_agent = SpecAgent()
matchmaker = MatchmakerAgent()

def main():
    st.title("Raw Material Development Assistant")
    
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
                    supplier_data = {
                        'name': supplier_name,
                        'chemical': chemical,
                        'purity': purity,
                        'delivery_rating': delivery_rating,
                        'min_order': min_order
                    }
                    try:
                        supplier_id = matchmaker.add_supplier(supplier_data)
                        st.success(f"Supplier added successfully with ID: {supplier_id}")
                    except Exception as e:
                        st.error(f"Error adding supplier: {str(e)}")

    # Main content
    st.header("Request for Quotation (RFQ)")
    rfq_text = st.text_area("Enter RFQ text:")
    
    if st.button("Process RFQ"):
        if rfq_text:
            try:
                specs = spec_agent.process_rfq(rfq_text)
                st.json(specs)
                
                if st.button("Find Suppliers"):
                    try:
                        suppliers = matchmaker.find_suppliers(specs)
                        st.subheader("Matching Suppliers")
                        for supplier in suppliers:
                            st.write(f"**{supplier['name']}**")
                            st.write(f"- Chemical: {supplier['chemical']}")
                            st.write(f"- Purity: {supplier['purity']}%")
                            st.write(f"- Delivery Rating: {supplier['delivery_rating']}/10")
                            st.write(f"- Minimum Order: {supplier['min_order']} kg")
                            st.write(f"- Score: {supplier['score']:.2f}")
                            st.write("---")
                    except Exception as e:
                        st.error(f"Error finding suppliers: {str(e)}")
            except Exception as e:
                st.error(f"Error processing RFQ: {str(e)}")

if __name__ == "__main__":
    main()
