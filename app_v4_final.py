import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.colors as mcolors
from pandas.io.formats.style import Styler
from plotly.subplots import make_subplots
import geopandas as gpd
import matplotlib

st.set_page_config(layout="wide")

##### LOGO ##########

# Assuming your logo is a local file. For a URL, just replace the path with the URL.
st.markdown(
    f"""
    <div style="text-align: center">
        <img src="https://raw.githubusercontent.com/luisaporrasm/DVA_GaTech/main/logo_DVA.png" width="180">
    </div>
    """,
    unsafe_allow_html=True
)

##### FONT ###########
css = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@400;700&display=swap');
    html, body, [class*="st-"] {{
        font-family: 'Roboto Condensed', sans-serif;
    }}
</style>
"""

# Inject CSS with markdown
st.markdown(css, unsafe_allow_html=True)

#### TITLE MIDDLE & DESCRIPTION #########

title_subtitle_css = """
<style>
.title-class {
    text-align: center;
    font-size: 80px;
    /* Additional styles if needed */
}

.subtitle-class {
    text-align: center;
    font-size: 30px; /* Subtitle font size */
    color: #E8F5E9; /* Subtitle text color */
    margin-top: 10px; /* Space between title and subtitle */
    margin-bottom: 20px; /* Space between subtitle and the rest of the content */
}

</style>
"""
st.markdown(title_subtitle_css, unsafe_allow_html=True)

st.markdown('<div class="title-class"><h1>Calgary Home Navigator: Dream, Decide, Dwell</h1></div>',
            unsafe_allow_html=True)

# Subtitle/Description
st.markdown('''
<div class="subtitle-class">
    <p><b>Dream Home or Smart Investment? Uncover Calgary's Best with our all-in-one affordability and market insight tool.</p>
    <p><b>Your journey to a savvy home choice starts here!<b></p>
</div>
''', unsafe_allow_html=True)

##### COLOR SLIDERS #######
# CSS in a Python multi-line string
slider_color_css = """
<style>
/* Target the slider track */
div[role="slider"] {
    background-color: #FF9100; /* This is the color of the slider track */
}

}
</style>
"""

# Use st.markdown to inject the defined CSS into the app
st.markdown(slider_color_css, unsafe_allow_html=True)

###### SUMMARY BOXES ##########

summary_box_css = """
<style>
.summary-box {
    background-color: #00695C;
    color: #ffffff; /*
    box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2); /* Optional: Adds a shadow for a 3D effect */
    border-radius: 10px; /* Optional: Rounds the corners of the rectangle */
    padding: 20px; /* Adds space inside the rectangle between content and border */
    margin: 10px 0; /* Adds space outside the rectangle between it and other elements */
}
</style>
"""

# Inject the CSS into the app
st.markdown(summary_box_css, unsafe_allow_html=True)

####### FRAME #############

custom_css = """
<style>
.framed-col {
    border: 2px solid #009688;  /* border style*/
    border-radius: 5px;         /* Optional: for rounded corners */
    padding: 10px;              /* Optional: for some internal padding */
    margin: 5px;                /* Optional: for some space around the columns */
}
</style>
"""
# Inject the CSS into Streamlit
st.markdown(custom_css, unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["Financial Fit Finder", "Buy vs. Rent Pathfinder", "Market Value Explorer", "Budget-Friendly Finds"])

# Content for Tab 1
with tab1:
    # st.write("This is the content of Tab 1")

    ######### FUNCTIONS CALCULATIONS ################################################################

    def calculate_stress_test_rate(base_rate, buffer, floor_rate):
        stress_test_rate = base_rate + buffer
        return max(stress_test_rate, floor_rate)


    def calculate_max_home_price(adjusted_monthly_income, annual_interest_rate, amortization_years, downpayment):
        # Apply stress test if required

        # Monthly interest rate. Assuming 2% buffer for the stress rate
        stress_test_rate = annual_interest_rate + 2
        monthly_interest_rate = stress_test_rate / 12 / 100  # converting percentage to decimal
        # Total number of payments
        total_payments = amortization_years * 12
        # Monthly payment for mortgage excluding taxes and insurance
        # estimated_taxes_insurance_per_month = adjusted_monthly_income * property_tax_and_insurance_rate / 12   # converting percentage to decimal
        # adjusted_monthly_income = adjusted_monthly_income - estimated_taxes_insurance_per_month
        # Maximum loan amount calculation
        max_loan_amount = (adjusted_monthly_income * (
                    1 - (1 + monthly_interest_rate) ** -total_payments)) / monthly_interest_rate
        # Estimated home price
        estimated_home_price = max_loan_amount / (1 - downpayment)  # (1-downpayment) is the loan amount

        return estimated_home_price


    def calculate_monthly_mortgage(loan_amount, annual_interest_rate, amortization_years):

        # Assuming 2% buffer for the interest rate
        stress_test_rate = annual_interest_rate + 2
        monthly_interest_rate = stress_test_rate / 12 / 100
        total_payments = amortization_years * 12
        monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** total_payments) / (
                    (1 + monthly_interest_rate) ** total_payments - 1)

        # Calculate total payment over the entire period
        total_payment = monthly_payment * total_payments

        # Calculate total interest paid
        total_interest_paid = total_payment - loan_amount

        return monthly_payment


    def calculate_mortgage_insurance(loan_amount, ltv_ratio):
        # Determine the insurance premium rate based on the LTV ratio
        if ltv_ratio <= 0.65:
            insurance_premium_rate = 0.0060  # 0.60%
        elif ltv_ratio <= 0.75:
            insurance_premium_rate = 0.0170  # 1.70%
        elif ltv_ratio <= 0.80:
            insurance_premium_rate = 0.0240  # 2.40%
        elif ltv_ratio <= 0.85:
            insurance_premium_rate = 0.0280  # 2.80%
        elif ltv_ratio <= 0.90:
            insurance_premium_rate = 0.0310  # 3.10%
        elif ltv_ratio <= 0.95:
            insurance_premium_rate = 0.0400  # 4.00%
        else:
            insurance_premium_rate = 0  #
        insurance_premium = loan_amount * insurance_premium_rate
        return insurance_premium


    def calculate_total_house_cost_with_interest(loan_amount, annual_interest_rate, amortization_years, downpayment):
        # Calculate the monthly mortgage payment
        monthly_payment = calculate_monthly_mortgage(loan_amount, annual_interest_rate, amortization_years)

        # Total number of payments
        total_payments = amortization_years * 12

        # Total amount paid over the loan period
        total_paid = monthly_payment * total_payments

        # Total cost of the house is the total paid plus the downpayment
        total_cost = total_paid + downpayment

        total_interest_paid = total_paid - loan_amount

        return total_cost, total_interest_paid


    def generate_data_interest(loan_amount, amortization_years, downpayment):
        interest_rates = [2, 3, 4, 5, 6, 7]
        data = []
        for rate in interest_rates:
            total_cost, total_interest_paid = calculate_total_house_cost_with_interest(loan_amount, rate,
                                                                                       amortization_years, downpayment)
            data.append([rate, total_cost, total_interest_paid])
        return data


    colors = ['#004D40', '#FFECB3', '#FFB74D']
    custom_cmap = mcolors.LinearSegmentedColormap.from_list('custom_cmap', colors, N=256)


    def style_table(df: pd.DataFrame) -> Styler:
        return df.style.format({
            'Total Cost': '${:,.0f}',
            'Total Interest Paid': '${:,.0f}'
        }) \
            .background_gradient(cmap=custom_cmap, subset=['Total Interest Paid']) \
            .background_gradient(cmap=custom_cmap, subset=['Total Cost']) \
            .set_properties(**{'text-align': 'center',
                               'width': '150px'}) \
            .set_table_styles([
            {'selector': 'th', 'props': [('text-align', 'center')]},
            {'selector': 'td', 'props': [('text-align', 'center')]}
        ])


    # Initialize variables that need to be accessed in both columns

    monthly_mortgage_payment = None
    stress_test_rate = None
    total_debt_payments = None
    insurance_table = []
    max_price = None
    downpayments_percentages = [0.0501, 0.10, 0.15, 0.20]

    ########################## MORTGAGE CALCULATOR ###############################

    col1, col2, col3 = st.columns([1.5, 1.8, 1.5])  # Adjust the ratio as needed

    # col1,col2, col3 = st.columns(3)

    with col1.container():
        # st.markdown('<div class="framed-col">', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #FFFDE7;">House Affordability Calculator</h2>', unsafe_allow_html=True)

        # Welcome message for the 'House Affordability Calculator' tab
        st.markdown(
            "Welcome to the 'House Affordability Calculator' - your personalized tool to determine the maximum house price you can afford based on your income, expenses, and mortgage details.")

        # Add an empty line (space) after the text
        st.write(" ")

        ### INCLUDE STRESS TEST  #####
        #### ADD THE INSURANCE IF DOWNPAYMENT IS LESS THAN 20%

        # User Inputs
        gross_income = st.number_input('Yearly Gross Income', min_value=0.0, value=100000.0, step=1000.0, format='%.2f',
                                       help='Enter your total yearly income before taxes')
        affordability_level = st.select_slider(
            'Affordability Level',
            options=([round(i * 0.1, 2) for i in range(0, 6)]),
            value=0.30,
            label_visibility="visible",
            help='Select how much of your disposable income is allocated to mortgage payments and monthly debt payments')
        annual_interest_rate = st.number_input('Annual Interest Rate (%)', min_value=0.0, value=4.0, step=0.1)
        amortization_years = st.number_input('Loan Term in Years', min_value=5, value=30, step=1,
                                             help='Amortization is the total time it takes to pay off your mortgage')
        downpayment = st.select_slider(
            'Down Payment',
            options=([round(i * 0.1, 2) for i in range(0, 9)]),
            value=0.20,
            label_visibility="visible",
            help='Down payment is a payment representing a fraction of the price of the property. In Canada, you can put as little as 5% down')

        ####### STRESS TEST ############################
        # New inputs for stress test and insurance calculation

        ############# OTHER DEBTS #######################
        # Checkbox to include debts
        include_debts = st.checkbox('Include Other Expenses (Debts)', False)

        # Conditional inputs for debts
        if include_debts:
            car_payment = st.number_input('Monthly Car Payment', min_value=0.0, value=0.0, step=50.0,
                                          help='Add up car loans or leases')
            credit_card_payment = st.number_input('Monthly Credit Card Payment', min_value=0.0, value=0.0, step=50.0,
                                                  help='Add up all monthly credit card payments')
            other_loans_payment = st.number_input('Monthly Other Loans Payment', min_value=0.0, value=0.0, step=50.0,
                                                  help='Add up all other personal loans or line of credit payments')
        else:
            car_payment = 0.0
            credit_card_payment = 0.0
            other_loans_payment = 0.0

        total_debt_payments = car_payment + credit_card_payment + other_loans_payment if include_debts else 0.0

        if st.button('Calculate Maximum House Price'):
            stress_test_rate = annual_interest_rate + 2
            monthly_gross_income = gross_income / 12
            monthly_available_income_house = monthly_gross_income - total_debt_payments
            adjusted_monthly_income = monthly_available_income_house * affordability_level
            max_price = calculate_max_home_price(adjusted_monthly_income, annual_interest_rate, amortization_years,
                                                 downpayment)

            st.session_state["estimated_home_price"] = max_price
            # st.success(f"The estimated maximum house price you can afford is: ${st.session_state.max_price:,.2f}")

            # Calculate loan amount
            loan_amount = max_price * (1 - downpayment)

            # Calculate LTV Ratio
            ltv_ratio = loan_amount / max_price

            # Monthly Mortgage Payment
            monthly_mortgage_payment = calculate_monthly_mortgage(loan_amount, annual_interest_rate, amortization_years)

            # insurance premium
            downpayment_amount = max_price * downpayment
            loan_amount = max_price - downpayment_amount
            ltv_ratio = loan_amount / max_price
            insurance_premium_property = calculate_mortgage_insurance(loan_amount, ltv_ratio)

            total_payments = amortization_years * 12
            monthly_insurance_premium_property = insurance_premium_property / total_payments

            # propery taxes: municipal and provincial
            monthly_property_tax_bill = ((max_price * 0.0043319) + (max_price * 0.0022399)) / 12

            # Mortgage Insurance Calculation for different downpayments
            downpayments_percentages = [0.0501, 0.10, 0.15, 0.20]

        # st.markdown('</div>', unsafe_allow_html=True)

    if monthly_mortgage_payment is not None:
        with col2.container():

            # st.markdown('<div class="framed-col">', unsafe_allow_html=True)

            # Create the HTML content string with your dynamic values
            if 'monthly_mortgage_payment' in locals():
                summary_html = f"""
                <div class="summary-box">
                    <h3>The estimated maximum house price you can afford is: $ {max_price:,.0f}</h3>
                    <p>Monthly Mortgage Payment: $ {monthly_mortgage_payment:,.0f}</p>
                    <p>Stress Test Rate (%): {stress_test_rate: .2f}</p>
                    <p>Monthly total Debt Payments: $ {total_debt_payments:,.0f}</p>
                    <p><br><b>Additional costs:</b><p>
                    <p> 2023 Monthly total property taxes (municipal and provincial): $ {monthly_property_tax_bill:,.0f} </p>
                    <p> 2023 Monthly Mortgage Insurance: $ {monthly_insurance_premium_property:,.0f} </p>
                </div>
                """

                # Display the HTML content with the custom styles applied
                st.markdown(summary_html, unsafe_allow_html=True)

            data = generate_data_interest(loan_amount, amortization_years, downpayment)
            df = pd.DataFrame(data, columns=['Interest Rate (%)', 'Total Cost', 'Total Interest Paid'])
            styled_df = style_table(df)
            st.write("**How much do you actually pay in interest?**")
            # Display the styled DataFrame
            # st.write(styled_df, unsafe_allow_html=True)
            st.table(styled_df)  # Or st.table(df) for a static table
            # st.markdown('</div>', unsafe_allow_html=True)

        # st.markdown('</div>', unsafe_allow_html=True)

        with col3.container():

            # st.markdown('<div class="framed-col">', unsafe_allow_html=True)

            # Define your color palette

            # Your expenses data
            expenses = {"Mortgage": monthly_mortgage_payment, "Property Taxes": monthly_property_tax_bill,
                        "Mortgage Insurance": monthly_insurance_premium_property}

            # Define your color palette
            color_palette = ['#00695C', '#FFECB3', '#FFB74D']

            # Your expenses data
            expenses = {
                "Mortgage": monthly_mortgage_payment,
                "Property Taxes": monthly_property_tax_bill,
                "Mortgage Insurance": monthly_insurance_premium_property
            }

            # Data preparation
            df = pd.DataFrame(expenses.items(), columns=['Category', 'Amount'])

            # Creating the pie chart
            fig = go.Figure(data=[go.Pie(
                labels=df['Category'],
                values=df['Amount'],
                marker_colors=color_palette,
                textinfo='label+percent',  # Shows the label and the percentage
                hole=0.3  # You can adjust the size of the hole in the middle
            )])

            # Customizing the layout
            fig.update_layout(
                title={
                    'text': 'Monthly Expenses Breakdown',
                    'y': 0.9,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                legend=dict(
                    x=0.85,
                    y=1.15,
                    xanchor='center',
                    yanchor='top'
                ),
                width=450,
                height=450,
                showlegend=True
            )

            # Display the plot in Streamlit
            st.plotly_chart(fig)

# Content for Tab 2
with tab2:
    # st.write("This is the content of Tab 2")

    import streamlit as st
    import streamlit.components.v1 as components
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import plotly.graph_objects as go
    import altair as alt


    def set_bg_color():
        st.markdown(
            f"""
            <style>
            .reportview-container {{
                background-color: #ADD8E6;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )


    # Define a function to calculate the liquid net worth over time (Buying Scenario)
    def calculate_buying_liquid_net_worth(purchase_price, down_payment_percent, mortgage_interest_rate,
                                          amortization_period, home_appreciation_rate, property_tax_percent,
                                          initial_annual_maintenance, monthly_utilities, monthly_insurance,
                                          monthly_condo_fees,
                                          other_monthly_payments, sale_transaction_costs_percent, lump_sum_fee,
                                          general_inflation_rate):

        down_payment = purchase_price * (down_payment_percent / 100)
        initial_loan_amount = purchase_price - down_payment

        # Add lump sum fee to the mortgage balance if down payment is less than 20%
        loan_amount = initial_loan_amount + lump_sum_fee if down_payment_percent < 20 else initial_loan_amount

        # Convert annual interest rate to monthly interest rate
        semi_annual_rate = mortgage_interest_rate / 2 / 100
        annual_effective_rate = (1 + semi_annual_rate) ** 2 - 1
        monthly_interest_rate = (1 + annual_effective_rate) ** (1 / 12) - 1
        total_payments = amortization_period * 12

        # Calculate monthly mortgage payment
        if mortgage_interest_rate == 0:
            monthly_payment = loan_amount / total_payments
        else:
            monthly_payment = loan_amount * monthly_interest_rate / (1 - (1 + monthly_interest_rate) ** -total_payments)

        buying_liquid_net_worth_over_time = {}
        current_mortgage_balance = loan_amount

        for year in range(amortization_period + 1):
            # Calculate home value
            current_home_value = purchase_price * (1 + home_appreciation_rate / 100) ** year

            # Reset interest and principal sums for the year
            annual_interest_sum = 0
            annual_principal_sum = 0

            for month in range(1, 13):
                if year > 0 and current_mortgage_balance > 0:
                    monthly_interest = current_mortgage_balance * monthly_interest_rate
                    monthly_principal = min(monthly_payment - monthly_interest, current_mortgage_balance)
                    current_mortgage_balance -= monthly_principal
                    annual_interest_sum += monthly_interest
                    annual_principal_sum += monthly_principal

            # Calculate annual expenses
            annual_property_tax = current_home_value * (property_tax_percent / 100) if year > 0 else 0
            annual_maintenance = initial_annual_maintenance * (
                        1 + general_inflation_rate / 100) ** year if year > 0 else 0
            annual_utilities = monthly_utilities * 12 if year > 0 else 0
            annual_insurance = monthly_insurance * 12 if year > 0 else 0
            annual_condo_fees = monthly_condo_fees * 12 if year > 0 else 0
            annual_other = other_monthly_payments * 12 if year > 0 else 0
            annual_housing_expense = monthly_payment * 12 + annual_property_tax + annual_maintenance + annual_utilities + annual_insurance + annual_condo_fees + annual_other

            # Calculate home equity and selling costs
            home_equity_pre_selling = current_home_value - current_mortgage_balance
            selling_costs = current_home_value * (sale_transaction_costs_percent / 100)
            home_equity_post_selling = home_equity_pre_selling - selling_costs

            # Store results in the dictionary
            buying_liquid_net_worth_over_time[year] = {
                "Home Value": current_home_value,
                "Mortgage Balance": current_mortgage_balance,
                "Home Equity Pre-Selling": home_equity_pre_selling,
                "Selling Costs": selling_costs,
                "Home Equity Post-Selling": home_equity_post_selling,
                "Annual Housing Expense": annual_housing_expense,
                "Implied Monthly Housing Expense": annual_housing_expense / 12,
                "Liquid Net Worth": home_equity_post_selling,
                "Interest Payment": annual_interest_sum,
                "Principal Payment": annual_principal_sum,
                "Annual Property Tax": annual_property_tax,
                "Annual Maintenance": annual_maintenance,
                "Annual Utilities": annual_utilities,
                "Annual Insurance": annual_insurance,
                "Annual Condo Fees": annual_condo_fees,
                "Annual Other": annual_other
            }

        return buying_liquid_net_worth_over_time, down_payment


    def calculate_rental_liquid_net_worth(home_purchase_costs, down_payment_amount, monthly_rent_payment,
                                          annual_rent_increase, monthly_utilities, monthly_renters_insurance,
                                          other_monthly_fees, annual_investment_return, buying_annual_housing_expenses):

        # Initial Investment Portfolio
        implied_initial_investment_portfolio = home_purchase_costs + down_payment_amount
        eop_investment_portfolio = implied_initial_investment_portfolio

        rental_liquid_net_worth_over_time = {}
        annual_rent_payment = monthly_rent_payment * 12

        for year in range(len(buying_annual_housing_expenses)):
            # BOP Investment Portfolio is the EOP from the previous year
            bop_investment_portfolio = eop_investment_portfolio

            # Calculate Annual Housing Expense for Renting
            annual_housing_expense_renting = annual_rent_payment + (
                        monthly_utilities + monthly_renters_insurance + other_monthly_fees) * 12

            if year > 0:
                # Adjust for rent increase from year 1 onwards
                annual_rent_payment *= (1 + annual_rent_increase / 100)
                # Incremental Cash Flows versus Buying
                incremental_cash_flows = max(0, -1 * annual_housing_expense_renting - (
                            -1 * buying_annual_housing_expenses[year]))
                # Investment Return
                investment_return = bop_investment_portfolio * (annual_investment_return / 100)
                # EOP Investment Portfolio Calculation
                eop_investment_portfolio = bop_investment_portfolio + incremental_cash_flows + investment_return
            else:
                # For year 0, there are no incremental cash flows or investment returns
                annual_housing_expense_renting = 0
                incremental_cash_flows = 0

            # Liquid Net Worth Calculation
            liquid_net_worth = eop_investment_portfolio

            rental_liquid_net_worth_over_time[year] = {
                "Annual Housing Expense Renting": annual_housing_expense_renting,
                "BOP Investment Portfolio": bop_investment_portfolio,
                "EOP Investment Portfolio": eop_investment_portfolio,
                "Incremental Cash Flow": incremental_cash_flows,
                "Liquid Net Worth": liquid_net_worth,
                "Annual Rent Payment": annual_rent_payment,
                "Annual Utilities": monthly_utilities * 12,
                "Annual Renters Insurance": monthly_renters_insurance * 12,
                "Other Annual Fees": other_monthly_fees * 12
            }

        return rental_liquid_net_worth_over_time


    # st.set_page_config(page_title="My App", layout='wide')

    def main():
        set_bg_color()
        st.markdown('<h2 style="color: #FFFDE7;">Buy vs. Rent Calculator</h2>', unsafe_allow_html=True)

        st.markdown(
            "Make an informed decision between buying and renting with our 'Buy vs. Rent Calculator'. Input your financial details to compare the long-term impact on your net worth, and see a clear visualization of potential financial outcomes over time.")

        # Add an empty line (space) after the text
        st.write(" ")

        # Initialize session_state variables if they are not already defined
        if 'general_inflation_rate' not in st.session_state:
            st.session_state.general_inflation_rate = 0.0

        if 'home_purchase_price' not in st.session_state:
            st.session_state.home_purchase_price = 0.0

        if 'down_payment_amount' not in st.session_state:
            st.session_state.down_payment_amount = 0.0

        if 'home_purchase_costs' not in st.session_state:
            st.session_state.home_purchase_costs = 0.0

        # Custom CSS to add padding on the left
        st.markdown("""
            <style>
            .reportview-container .main .block-container {
                padding-left: 5rem;  /* Adjust the value as needed */
            }
            /* Decrease the vertical spacing */
            .row-widget.stRadio > div {
                margin: 0;  /* Adjust vertical spacing for radio buttons */
            }
            .block-container > div {
                margin-bottom: -20px;  /* Adjust vertical spacing for other widgets */
            }
            /* Position the question mark icon */
            .tooltip-icon {
                display: inline-block;
                position: relative;
                top: -26px;  /* Adjust vertical position */
                left: 5px;   /* Adjust horizontal position */
            }
            </style>
            """, unsafe_allow_html=True)

        # Define your columns
        buffer, col2, col3 = st.columns([1.5, 1.5, 4])

        # Initialize the variables
        years = []
        net_worth_values = []
        home_values = []
        mortgage_balances = []

        with buffer:
            with st.form("buying_inputs"):
                st.markdown("### Buying Scenario Assumptions")  # Larger header
                # st.header("Buying Scenario Assumptions")

                # def info_icon(tooltip_text):
                #     # Styling the question mark to be white, bold, and to the right top of the input box
                #     html_str = f"""
                #     <span class="tooltip-icon" title="{tooltip_text}" style="font-size: 20px; font-weight: bold; color: white; cursor: pointer;">?</span>
                #     """
                #     return components.html(html_str, height=30)

                # Home Purchase Price
                st.session_state.home_purchase_price = st.number_input("Home Purchase Price ($)",
                                                                       value=st.session_state.home_purchase_price,
                                                                       min_value=0.0,
                                                                       help="Enter the purchase price of the home. This is the total amount you will pay for the property.")
                # info_icon("Enter the purchase price of the home. This is the total amount you will pay for the property.")

                # Down Payment Percent
                down_payment_percent = st.number_input("Down Payment as a % of Home Value", min_value=0.0,
                                                       max_value=100.0,
                                                       value=5.0,
                                                       help="Enter the percentage of the home's value that you will pay as a down payment.")

                # Determine Mortgage Insurance Need and Lump Sum Fee
                if down_payment_percent < 20:
                    mortgage_insurance_needed = "Yes"
                    lump_sum_fee = st.number_input("Lump Sum Fee Added to Mortgage Balance ($)", value=2000.0,
                                                   help="Enter the lump sum fee that will be added to the mortgage balance. This is the fee charged by the lender for mortgage insurance. If down payment is less than 20%, mortgage insurance is required.")
                else:
                    mortgage_insurance_needed = "No"
                    lump_sum_fee = 0.0  # Set lump sum fee to zero if down payment is 20% or more

                # Display mortgage insurance requirement (optional)
                st.write(f"Mortgage Insurance Needed: {mortgage_insurance_needed}")

                # Annual Home Value Appreciation
                annual_home_appreciation = st.number_input("Annual Home Value Appreciation (%)", min_value=0.0, value=4.0,
                                                           help="Enter the expected annual rate at which your home's value will increase.")
                # info_icon("Enter the expected annual rate at which your home's value will increase.")

                # Average Mortgage Interest Rate
                mortgage_interest_rate = st.number_input("Average Mortgage Interest Rate (%)", min_value=0.0, value=5.0,
                                                         help="Enter the average interest rate for your mortgage over its entire term.")
                # info_icon("Enter the average interest rate for your mortgage over its entire term.")

                # Mortgage Amortization Period
                mortgage_amortization = st.number_input("Mortgage Amortization Period (years)", min_value=1, value=25,
                                                        help="Enter the number of years over which the mortgage will be fully repaid.")
                # info_icon("Enter the number of years over which the mortgage will be fully repaid.")

                # Annual Property Tax Percent
                annual_property_tax_percent = st.number_input("Annual Property Tax as a % of Home Value (%)",
                                                              min_value=0.0,
                                                              value=1.0,
                                                              help="Enter the annual property tax rate as a percentage of your home's value.")
                # info_icon("Enter the annual property tax rate as a percentage of your home's value.")

                # Annual Home Maintenance
                initial_annual_maintenance = st.number_input("Annual Home Maintenance ($ per year)", min_value=0.0, value=2000.0,
                                                             help="Enter the estimated annual cost for home repairs, upgrades, and regular maintenance.")
                # info_icon("Enter the estimated annual cost for home repairs, upgrades, and regular maintenance.")

                # Monthly Utilities Payment
                monthly_utilities = st.number_input("Monthly Utilities Payment ($ per month)", min_value=0.0, value=300.0,
                                                    help="Enter your estimated monthly cost for utilities like heat, electricity, and water.")
                # info_icon("Enter your estimated monthly cost for utilities like heat, electricity, and water.")

                # Monthly Homeowner's Insurance Payment
                monthly_insurance = st.number_input("Monthly Homeowner's Insurance Payment ($ per month)",
                                                    min_value=0.0,
                                                    value=100.0,
                                                    help="Enter the monthly cost of your homeowner's insurance.")
                # info_icon("Enter the monthly cost of your homeowner's insurance.")

                # Monthly Condo Fee Payment
                monthly_condo_fees = st.number_input("Monthly Condo Fee Payment ($ per month)", value=0.0,
                                                     help="If applicable, enter your monthly condo fees. Default is zero.")
                # info_icon("If applicable, enter your monthly condo fees. Default is zero.")

                # Other Monthly Payments
                other_monthly_payments = st.number_input("Other Monthly Payments ($ per month)", value=0.0,
                                                         help="Enter any other monthly payments related to your home.")
                # info_icon("Enter any other monthly payments related to your home.")

                # Home Purchase Transaction Costs
                st.session_state.home_purchase_costs = st.number_input("Home Purchase Transaction Costs ($)",
                                                                       value=st.session_state.home_purchase_costs,
                                                                       min_value=0.0,
                                                                       help="Enter one-time costs paid during the home purchase like land transfer tax, legal fees, and home inspection.")
                # info_icon("Enter one-time costs paid during the home purchase like land transfer tax, legal fees, and home inspection.")

                # Home Sale Transaction Costs Percent
                home_sale_costs_percent = st.number_input("Home Sale Transaction Costs as a % of Home Value (%)",
                                                          min_value=0.0,
                                                          value=4.0,
                                                          help="Enter the percentage of the home's value that will be paid as transaction costs when selling the home.")
                # info_icon("Enter the percentage of the home's value that will be paid as transaction costs when selling the home.")

                submit_button = st.form_submit_button(label='Calculate')

                if submit_button:
                    # Perform calculation
                    liquid_net_worth, down_payment_amount = calculate_buying_liquid_net_worth(
                        st.session_state.home_purchase_price, down_payment_percent, mortgage_interest_rate,
                        mortgage_amortization, annual_home_appreciation, annual_property_tax_percent,
                        initial_annual_maintenance, monthly_utilities, monthly_insurance, monthly_condo_fees,
                        other_monthly_payments, home_sale_costs_percent, lump_sum_fee,
                        st.session_state.general_inflation_rate)

                    # Store the calculated down payment amount in session_state
                    st.session_state.down_payment_amount = down_payment_amount
                    st.session_state.liquid_net_worth = liquid_net_worth

                    # # Display the results
                    # st.write("Buying Liquid Net Worth Over Time:")
                    # for year, data in liquid_net_worth.items():
                    #     st.write(f"Year {year}:")
                    #     st.write(f"Home Value: ${data['Home Value']:,.2f}")
                    #     st.write(f"Mortgage Balance: ${data['Mortgage Balance']:,.2f}")
                    #     st.write(f"Home Equity (Pre-Selling): ${data['Home Equity Pre-Selling']:,.2f}")
                    #     st.write(f"Selling Costs: ${data['Selling Costs']:,.2f}")
                    #     st.write(f"Home Equity (Post-Selling): ${data['Home Equity Post-Selling']:,.2f}")
                    #     st.write(f"Annual Housing Expense: ${data['Annual Housing Expense']:,.2f}")
                    #     st.write(f"Monthly Housing Expense: ${data['Implied Monthly Housing Expense']:,.2f}")
                    #     st.write(f"Liquid Net Worth: ${data['Liquid Net Worth']:,.2f}")
                    #     st.write(f"Interest Payment: ${data['Interest Payment']:,.2f}")
                    #     st.write(f"Principal Payment: ${data['Principal Payment']:,.2f}")
                    #     st.write("---")  # Add a separator for readability

                    # Prepare data for plotting
                    years = list(liquid_net_worth.keys())
                    net_worth_values = [data['Liquid Net Worth'] for data in liquid_net_worth.values()]
                    home_values = [data['Home Value'] for data in liquid_net_worth.values()]
                    mortgage_balances = [data['Mortgage Balance'] for data in liquid_net_worth.values()]
                    interest_payments = [data['Interest Payment'] for data in liquid_net_worth.values()]
                    principal_payments = [data['Principal Payment'] for data in liquid_net_worth.values()]

                    interest_payments_cum = np.cumsum(interest_payments)
                    principal_payments_cum = np.cumsum(principal_payments)

        # Other columns can be used for additional content if needed
        with col2:
            st.markdown("### Rental Scenario Assumptions")
            # st.header("Rental Scenario Assumptions")
            st.write("\n")

            monthly_rent_payment = st.number_input("Monthly Rent Payment ($ per month)", min_value=0.0, value=2000.0,
                                                   help="Enter your monthly rent payment.")
            annual_rent_increase = st.number_input("Annual Rent Increase (%)", min_value=0.0, value=2.0,
                                                   help="Enter the expected annual rate at which your rent will increase.")
            monthly_utilities_rental = st.number_input("Monthly Utilities Payment (Rental) ($ per month)",
                                                       min_value=0.0, value=150.0,
                                                       help="Enter your estimated monthly cost for utilities like heat, electricity, and water.")
            monthly_renters_insurance = st.number_input("Monthly Renter's Insurance Payment ($ per month)",
                                                        min_value=0.0, value=50.0,
                                                        help="Enter the monthly cost of your renter's insurance.")
            other_monthly_payments_rental = st.number_input("Other Monthly Payments (Rental) ($ per month)",
                                                            min_value=0.0,
                                                            help="Enter any other monthly payments related to your rental.")
            annual_investment_return = st.number_input("Annual After-Tax Investment Return (Nominal) (%)",
                                                       min_value=0.0,
                                                       help="Enter the expected annual after-tax investment return on your investment portfolio.")
            st.session_state.general_inflation_rate = st.number_input("General Inflation Rate (%)",
                                                                      value=st.session_state.general_inflation_rate,
                                                                      min_value=0.0,
                                                                      help="Enter the expected annual inflation rate.")

            # Add a separate button for Rental Scenario or use the same 'Calculate' button
            # If using the same button, ensure it's outside the form

            # Rental Scenario Calculations
            if submit_button:
                # Extract the annual housing expense from the buying results for comparison
                buying_annual_housing_expenses = [data['Annual Housing Expense'] for data in
                                                  st.session_state.liquid_net_worth.values()]

                # st.write("General Inflation Rate: ", st.session_state.general_inflation_rate)
                # st.write("Home Purchase Price: ", st.session_state.home_purchase_price)
                # st.write("Down Payment Amount: ", st.session_state.down_payment_amount)
                # st.write("Home Purchase Costs: ", st.session_state.home_purchase_costs)

                # Calculate the Rental Liquid Net Worth
                rental_results = calculate_rental_liquid_net_worth(st.session_state.home_purchase_costs,
                                                                   st.session_state.down_payment_amount,
                                                                   monthly_rent_payment,
                                                                   annual_rent_increase, monthly_utilities_rental,
                                                                   monthly_renters_insurance,
                                                                   other_monthly_payments_rental,
                                                                   annual_investment_return,
                                                                   buying_annual_housing_expenses)

                # # Display the results
                # st.write("Rental Liquid Net Worth Over Time:")
                # for year, data in rental_results.items():
                #     st.write(f"Year {year}:")
                #     st.write(f"Annual Housing Expense (Renting): ${data['Annual Housing Expense Renting']:,.2f}")
                #     st.write(f"BOP Investment Portfolio: ${data['BOP Investment Portfolio']:,.2f}")
                #     st.write(f"EOP Investment Portfolio: ${data['EOP Investment Portfolio']:,.2f}")
                #     st.write(f"Incremental Cash Flow: ${data['Incremental Cash Flow']:,.2f}")
                #     st.write(f"Liquid Net Worth: ${data['Liquid Net Worth']:,.2f}")
                #     st.write("---")  # Add a separator for readability

        with col3:
            # st.write("This is in column 3")

            if submit_button:

                buying_liquid_net_worth, down_payment_amount = calculate_buying_liquid_net_worth(
                    st.session_state.home_purchase_price, down_payment_percent, mortgage_interest_rate,
                    mortgage_amortization, annual_home_appreciation, annual_property_tax_percent,
                    initial_annual_maintenance, monthly_utilities, monthly_insurance, monthly_condo_fees,
                    other_monthly_payments, home_sale_costs_percent, lump_sum_fee,
                    st.session_state.general_inflation_rate)

                rental_liquid_net_worth = calculate_rental_liquid_net_worth(st.session_state.home_purchase_costs,
                                                                            st.session_state.down_payment_amount,
                                                                            monthly_rent_payment,
                                                                            annual_rent_increase,
                                                                            monthly_utilities_rental,
                                                                            monthly_renters_insurance,
                                                                            other_monthly_payments_rental,
                                                                            annual_investment_return,
                                                                            buying_annual_housing_expenses)

                # crossover_month = None
                # crossover_time = None

                # # Loop through the years to find the crossover interval
                # for year in range(mortgage_amortization - 1):
                #     buying_current_year = buying_liquid_net_worth[year]["Liquid Net Worth"]
                #     buying_next_year = buying_liquid_net_worth[year + 1]["Liquid Net Worth"]
                #     rental_current_year = rental_liquid_net_worth[year]["Liquid Net Worth"]
                #     rental_next_year = rental_liquid_net_worth[year + 1]["Liquid Net Worth"]

                #     if buying_current_year < rental_current_year and buying_next_year >= rental_next_year:
                #         # Interpolate within this year range
                #         for month in range(1, 13):  # Check each month
                #             fraction_of_year = month / 12.0
                #             interpolated_buying = buying_current_year + (buying_next_year - buying_current_year) * fraction_of_year
                #             interpolated_rental = rental_current_year + (rental_next_year - rental_current_year) * fraction_of_year

                #             if interpolated_buying >= interpolated_rental:
                #                 crossover_month = month
                #                 crossover_time = year + fraction_of_year
                #                 break

                #         if crossover_month is not None:
                #             break

                # if crossover_time is not None:
                #     st.markdown(f"""
                #     <style>
                #         .highlight {{
                #             font-size: 20px;
                #             color: red;
                #         }}
                #     </style>
                #     <p>Initially, renting is the better option. After <span class='highlight'>~{crossover_time:.2f} years</span>, buying becomes the better option.</p>
                #     """, unsafe_allow_html=True)

                # # if crossover_time is not None:
                # #     st.write(f"Initially, renting is the better option. After ~{crossover_time:.2f} years, buying becomes the better option.")
                # else:
                #     st.write("No crossover detected within the amortization period.")

                # Extract Rental Liquid Net Worth values
                rental_net_worth_values = [data['Liquid Net Worth'] for data in rental_results.values()]

                # Initialize a list to store the differences
                net_worth_differences = []

                # Calculate the difference for each year
                for year in years:
                    buying_net_worth = buying_liquid_net_worth[year]["Liquid Net Worth"]
                    rental_net_worth = rental_liquid_net_worth[year]["Liquid Net Worth"]
                    difference = - buying_net_worth + rental_net_worth
                    net_worth_differences.append(difference)

                    # Optionally, display the difference per year
                    # st.write(f"Year {year} Difference: ${difference:,.2f}")

            plot_option = st.selectbox(
                'Select a plot to view',
                ('Buying vs Renting Net Worth', 'Home Value and Mortgage Balance', 'Annual Housing Expense Comparison',
                 'Annual Housing Expense - Buying', 'Annual Housing Expense - Renting', 'Tables - Calculated Results')
            )

            st.write('\n')

            # Buying vs Renting Net Worth
            if plot_option == 'Buying vs Renting Net Worth':

                buying_liquid_net_worth, down_payment_amount = calculate_buying_liquid_net_worth(
                    st.session_state.home_purchase_price, down_payment_percent, mortgage_interest_rate,
                    mortgage_amortization, annual_home_appreciation, annual_property_tax_percent,
                    initial_annual_maintenance, monthly_utilities, monthly_insurance, monthly_condo_fees,
                    other_monthly_payments, home_sale_costs_percent, lump_sum_fee,
                    st.session_state.general_inflation_rate)

                buying_annual_housing_expenses = [data['Annual Housing Expense'] for data in
                                                  buying_liquid_net_worth.values()]

                rental_liquid_net_worth = calculate_rental_liquid_net_worth(st.session_state.home_purchase_costs,
                                                                            st.session_state.down_payment_amount,
                                                                            monthly_rent_payment,
                                                                            annual_rent_increase,
                                                                            monthly_utilities_rental,
                                                                            monthly_renters_insurance,
                                                                            other_monthly_payments_rental,
                                                                            annual_investment_return,
                                                                            buying_annual_housing_expenses)

                crossover_month = None
                crossover_time = None

                # Loop through the years to find the crossover interval
                for year in range(mortgage_amortization - 1):
                    buying_current_year = buying_liquid_net_worth[year]["Liquid Net Worth"]
                    buying_next_year = buying_liquid_net_worth[year + 1]["Liquid Net Worth"]
                    rental_current_year = rental_liquid_net_worth[year]["Liquid Net Worth"]
                    rental_next_year = rental_liquid_net_worth[year + 1]["Liquid Net Worth"]

                    if buying_current_year < rental_current_year and buying_next_year >= rental_next_year:
                        # Interpolate within this year range
                        for month in range(1, 13):  # Check each month
                            fraction_of_year = month / 12.0
                            interpolated_buying = buying_current_year + (
                                        buying_next_year - buying_current_year) * fraction_of_year
                            interpolated_rental = rental_current_year + (
                                        rental_next_year - rental_current_year) * fraction_of_year

                            if interpolated_buying >= interpolated_rental:
                                crossover_month = month
                                crossover_time = year + fraction_of_year
                                break

                        if crossover_month is not None:
                            break

                if crossover_time is not None:
                    st.markdown(f"""
                    <style>
                        .highlight {{
                            font-size: 30px;  /* Font size for the highlighted span */
                            color: red;
                        }}
                        .custom-text {{
                            font-size: 25px;  /* Font size for the entire paragraph */
                        }}
                    </style>
                    <p class='custom-text'>Initially, renting is the better option. After <span class='highlight'>~{crossover_time:.2f} years</span>, buying becomes the better option.</p>
                    """, unsafe_allow_html=True)

                else:
                    st.markdown(f"""
                    <style>
                        .custom-text {{
                            font-size: 25px;  /* Font size for the entire paragraph */
                        }}
                    </style>
                    <p class='custom-text'>No crossover detected within the amortization period.</p>
                    """, unsafe_allow_html=True)

                st.write('\n')

                # Create Buying Scenario Dataframe
                buying_df = pd.DataFrame({
                    "Year": list(range(mortgage_amortization + 1)),
                    "Home Value": [data["Home Value"] for data in buying_liquid_net_worth.values()],
                    "Mortgage Balance": [data["Mortgage Balance"] for data in buying_liquid_net_worth.values()],
                    "Home Equity (Pre-Selling)": [data["Home Equity Pre-Selling"] for data in
                                                  buying_liquid_net_worth.values()],
                    "Selling Costs": [data["Selling Costs"] for data in buying_liquid_net_worth.values()],
                    "Home Equity (Post-Selling)": [data["Home Equity Post-Selling"] for data in
                                                   buying_liquid_net_worth.values()],
                    "Annual Housing Expense": [data["Annual Housing Expense"] for data in
                                               buying_liquid_net_worth.values()],
                    "Monthly Housing Expense": [data["Implied Monthly Housing Expense"] for data in
                                                buying_liquid_net_worth.values()],
                    "Interest Payment": [data["Interest Payment"] for data in buying_liquid_net_worth.values()],
                    "Principal Payment": [data["Principal Payment"] for data in buying_liquid_net_worth.values()],
                    "Liquid Net Worth": [data["Liquid Net Worth"] for data in buying_liquid_net_worth.values()]
                })

                # Create Renting Scenario Dataframe
                renting_df = pd.DataFrame({
                    "Year": list(range(mortgage_amortization + 1)),
                    "Annual Housing Expense Renting": [data["Annual Housing Expense Renting"] for data in
                                                       rental_liquid_net_worth.values()],
                    "BOP Investment Portfolio": [data["BOP Investment Portfolio"] for data in
                                                 rental_liquid_net_worth.values()],
                    "EOP Investment Portfolio": [data["EOP Investment Portfolio"] for data in
                                                 rental_liquid_net_worth.values()],
                    "Liquid Net Worth": [data["Liquid Net Worth"] for data in rental_liquid_net_worth.values()]
                })

                # Prepare data for plotting
                years = list(buying_liquid_net_worth.keys())
                net_worth_values = [data['Liquid Net Worth'] for data in buying_liquid_net_worth.values()]
                home_values = [data['Home Value'] for data in buying_liquid_net_worth.values()]
                mortgage_balances = [data['Mortgage Balance'] for data in buying_liquid_net_worth.values()]
                interest_payments = [data['Interest Payment'] for data in buying_liquid_net_worth.values()]
                principal_payments = [data['Principal Payment'] for data in buying_liquid_net_worth.values()]

                interest_payments_cum = np.cumsum(interest_payments)
                principal_payments_cum = np.cumsum(principal_payments)

                rental_net_worth_values = [data['Liquid Net Worth'] for data in rental_liquid_net_worth.values()]

                # Extract Rental Liquid Net Worth values
                rental_net_worth_values = [data['Liquid Net Worth'] for data in rental_liquid_net_worth.values()]

                # Initialize a list to store the differences
                net_worth_differences = []

                # Calculate the difference for each year
                for year in years:
                    buying_net_worth = buying_liquid_net_worth[year]["Liquid Net Worth"]
                    rental_net_worth = rental_liquid_net_worth[year]["Liquid Net Worth"]
                    difference = - buying_net_worth + rental_net_worth
                    net_worth_differences.append(difference)

                    # ['#004D40', '#FFECB3', '#FFB74D']

                if years:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=years, y=net_worth_values, mode='lines+markers', name='Buy',
                                             marker_color='#FFD740'))
                    fig.add_trace(go.Scatter(x=years, y=rental_net_worth_values, mode='lines+markers', name='Rent',
                                             marker_color='#FF6F00'))
                    # fig.add_trace(go.Scatter(x=years, y=home_values, mode='lines+markers', name='Home Value'))
                    # fig.add_trace(go.Scatter(x=years, y=mortgage_balances, mode='lines+markers', name='Mortgage Balance'))
                    fig.add_trace(go.Scatter(x=years, y=net_worth_differences, mode='lines+markers',
                                             name='Difference in Net Worth', marker_color='#00BFA5'))

                    fig.update_layout(
                        title='Liquid Net Worth Over Time',
                        xaxis_title='Year',
                        yaxis_title='Amount ($)',
                        width=800,  # Width of the figure in pixels
                        height=600  # Height of the figure in pixels
                    )

                    st.plotly_chart(fig, use_container_width=True)

            # Home Value and Mortgage Balance
            elif plot_option == 'Home Value and Mortgage Balance':

                buying_annual_housing_expenses = [data['Annual Housing Expense'] for data in
                                                  st.session_state.liquid_net_worth.values()]

                buying_liquid_net_worth, down_payment_amount = calculate_buying_liquid_net_worth(
                    st.session_state.home_purchase_price, down_payment_percent, mortgage_interest_rate,
                    mortgage_amortization, annual_home_appreciation, annual_property_tax_percent,
                    initial_annual_maintenance, monthly_utilities, monthly_insurance, monthly_condo_fees,
                    other_monthly_payments, home_sale_costs_percent, lump_sum_fee,
                    st.session_state.general_inflation_rate)

                rental_liquid_net_worth = calculate_rental_liquid_net_worth(st.session_state.home_purchase_costs,
                                                                            st.session_state.down_payment_amount,
                                                                            monthly_rent_payment,
                                                                            annual_rent_increase,
                                                                            monthly_utilities_rental,
                                                                            monthly_renters_insurance,
                                                                            other_monthly_payments_rental,
                                                                            annual_investment_return,
                                                                            buying_annual_housing_expenses)

                crossover_month = None
                crossover_time = None

                # Loop through the years to find the crossover interval
                for year in range(mortgage_amortization - 1):
                    buying_current_year = buying_liquid_net_worth[year]["Liquid Net Worth"]
                    buying_next_year = buying_liquid_net_worth[year + 1]["Liquid Net Worth"]
                    rental_current_year = rental_liquid_net_worth[year]["Liquid Net Worth"]
                    rental_next_year = rental_liquid_net_worth[year + 1]["Liquid Net Worth"]

                    if buying_current_year < rental_current_year and buying_next_year >= rental_next_year:
                        # Interpolate within this year range
                        for month in range(1, 13):  # Check each month
                            fraction_of_year = month / 12.0
                            interpolated_buying = buying_current_year + (
                                        buying_next_year - buying_current_year) * fraction_of_year
                            interpolated_rental = rental_current_year + (
                                        rental_next_year - rental_current_year) * fraction_of_year

                            if interpolated_buying >= interpolated_rental:
                                crossover_month = month
                                crossover_time = year + fraction_of_year
                                break

                        if crossover_month is not None:
                            break

                if crossover_time is not None:
                    st.markdown(f"""
                    <style>
                        .highlight {{
                            font-size: 30px;  /* Font size for the highlighted span */
                            color: red;
                        }}
                        .custom-text {{
                            font-size: 25px;  /* Font size for the entire paragraph */
                        }}
                    </style>
                    <p class='custom-text'>Initially, renting is the better option. After <span class='highlight'>~{crossover_time:.2f} years</span>, buying becomes the better option.</p>
                    """, unsafe_allow_html=True)

                else:
                    st.markdown(f"""
                    <style>
                        .custom-text {{
                            font-size: 25px;  /* Font size for the entire paragraph */
                        }}
                    </style>
                    <p class='custom-text'>No crossover detected within the amortization period.</p>
                    """, unsafe_allow_html=True)

                st.write('\n')

                years = list(buying_liquid_net_worth.keys())
                net_worth_values = [data['Liquid Net Worth'] for data in buying_liquid_net_worth.values()]
                home_values = [data['Home Value'] for data in buying_liquid_net_worth.values()]
                mortgage_balances = [data['Mortgage Balance'] for data in buying_liquid_net_worth.values()]
                interest_payments = [data['Interest Payment'] for data in buying_liquid_net_worth.values()]
                principal_payments = [data['Principal Payment'] for data in buying_liquid_net_worth.values()]

                interest_payments_cum = np.cumsum(interest_payments)
                principal_payments_cum = np.cumsum(principal_payments)

                if years:
                    fig = go.Figure()
                    # fig.add_trace(go.Scatter(x=years, y=net_worth_values, mode='lines+markers', name='Buy'))
                    fig.add_trace(go.Scatter(x=years, y=home_values, mode='lines+markers', name='Home Value'))
                    fig.add_trace(
                        go.Scatter(x=years, y=mortgage_balances, mode='lines+markers', name='Mortgage Balance'))
                    fig.add_trace(
                        go.Scatter(x=years, y=interest_payments_cum, mode='lines+markers', name='Interest Payments'))
                    fig.add_trace(
                        go.Scatter(x=years, y=principal_payments_cum, mode='lines+markers', name='Principal Payments'))

                    fig.update_layout(
                        title='Home Value and Mortgage Balance Over Time',
                        xaxis_title='Year',
                        yaxis_title='Amount ($)',
                        width=800,  # Width of the figure in pixels
                        height=600  # Height of the figure in pixels
                    )

                    st.plotly_chart(fig, use_container_width=True)

                # Annual Housing Expense Comparison
            elif plot_option == 'Annual Housing Expense Comparison':

                buying_annual_housing_expenses = [data['Annual Housing Expense'] for data in
                                                  st.session_state.liquid_net_worth.values()]

                buying_liquid_net_worth, down_payment_amount = calculate_buying_liquid_net_worth(
                    st.session_state.home_purchase_price, down_payment_percent, mortgage_interest_rate,
                    mortgage_amortization, annual_home_appreciation, annual_property_tax_percent,
                    initial_annual_maintenance, monthly_utilities, monthly_insurance, monthly_condo_fees,
                    other_monthly_payments, home_sale_costs_percent, lump_sum_fee,
                    st.session_state.general_inflation_rate)

                rental_liquid_net_worth = calculate_rental_liquid_net_worth(st.session_state.home_purchase_costs,
                                                                            st.session_state.down_payment_amount,
                                                                            monthly_rent_payment,
                                                                            annual_rent_increase,
                                                                            monthly_utilities_rental,
                                                                            monthly_renters_insurance,
                                                                            other_monthly_payments_rental,
                                                                            annual_investment_return,
                                                                            buying_annual_housing_expenses)

                crossover_month = None
                crossover_time = None

                # Loop through the years to find the crossover interval
                for year in range(mortgage_amortization - 1):
                    buying_current_year = buying_liquid_net_worth[year]["Liquid Net Worth"]
                    buying_next_year = buying_liquid_net_worth[year + 1]["Liquid Net Worth"]
                    rental_current_year = rental_liquid_net_worth[year]["Liquid Net Worth"]
                    rental_next_year = rental_liquid_net_worth[year + 1]["Liquid Net Worth"]

                    if buying_current_year < rental_current_year and buying_next_year >= rental_next_year:
                        # Interpolate within this year range
                        for month in range(1, 13):  # Check each month
                            fraction_of_year = month / 12.0
                            interpolated_buying = buying_current_year + (
                                        buying_next_year - buying_current_year) * fraction_of_year
                            interpolated_rental = rental_current_year + (
                                        rental_next_year - rental_current_year) * fraction_of_year

                            if interpolated_buying >= interpolated_rental:
                                crossover_month = month
                                crossover_time = year + fraction_of_year
                                break

                        if crossover_month is not None:
                            break

                if crossover_time is not None:
                    st.markdown(f"""
                    <style>
                        .highlight {{
                            font-size: 30px;  /* Font size for the highlighted span */
                            color: red;
                        }}
                        .custom-text {{
                            font-size: 25px;  /* Font size for the entire paragraph */
                        }}
                    </style>
                    <p class='custom-text'>Initially, renting is the better option. After <span class='highlight'>~{crossover_time:.2f} years</span>, buying becomes the better option.</p>
                    """, unsafe_allow_html=True)

                else:
                    st.markdown(f"""
                    <style>
                        .custom-text {{
                            font-size: 25px;  /* Font size for the entire paragraph */
                        }}
                    </style>
                    <p class='custom-text'>No crossover detected within the amortization period.</p>
                    """, unsafe_allow_html=True)

                st.write('\n')

                # Create Buying Scenario Dataframe
                buying_df = pd.DataFrame({
                    "Year": list(range(mortgage_amortization + 1)),
                    "Home Value": [data["Home Value"] for data in buying_liquid_net_worth.values()],
                    "Mortgage Balance": [data["Mortgage Balance"] for data in buying_liquid_net_worth.values()],
                    "Home Equity (Pre-Selling)": [data["Home Equity Pre-Selling"] for data in
                                                  buying_liquid_net_worth.values()],
                    "Selling Costs": [data["Selling Costs"] for data in buying_liquid_net_worth.values()],
                    "Home Equity (Post-Selling)": [data["Home Equity Post-Selling"] for data in
                                                   buying_liquid_net_worth.values()],
                    "Annual Housing Expense": [data["Annual Housing Expense"] for data in
                                               buying_liquid_net_worth.values()],
                    "Monthly Housing Expense": [data["Implied Monthly Housing Expense"] for data in
                                                buying_liquid_net_worth.values()],
                    "Interest Payment": [data["Interest Payment"] for data in buying_liquid_net_worth.values()],
                    "Principal Payment": [data["Principal Payment"] for data in buying_liquid_net_worth.values()],
                    "Liquid Net Worth": [data["Liquid Net Worth"] for data in buying_liquid_net_worth.values()]
                })

                # Create Renting Scenario Dataframe
                renting_df = pd.DataFrame({
                    "Year": list(range(mortgage_amortization + 1)),
                    "Annual Housing Expense Renting": [data["Annual Housing Expense Renting"] for data in
                                                       rental_liquid_net_worth.values()],
                    "BOP Investment Portfolio": [data["BOP Investment Portfolio"] for data in
                                                 rental_liquid_net_worth.values()],
                    "EOP Investment Portfolio": [data["EOP Investment Portfolio"] for data in
                                                 rental_liquid_net_worth.values()],
                    "Liquid Net Worth": [data["Liquid Net Worth"] for data in rental_liquid_net_worth.values()]
                })

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=buying_df['Year'],
                    y=buying_df['Annual Housing Expense'],
                    name='Buying',
                    marker_color='blue'
                ))
                fig.add_trace(go.Bar(
                    x=renting_df['Year'],
                    y=renting_df['Annual Housing Expense Renting'],
                    name='Renting',
                    marker_color='red'
                ))

                # Update layout
                fig.update_layout(
                    title='Comparison of Annual Housing Expenses: Buying vs Renting',
                    xaxis=dict(
                        title='Year',
                        titlefont_size=16,
                        tickfont_size=14),
                    yaxis=dict(
                        title='Annual Housing Expense ($)',
                        titlefont_size=16,
                        tickfont_size=14,
                    ),
                    legend=dict(
                        x=0,
                        y=1.0,
                        bgcolor='rgba(255, 255, 255, 0)',
                        bordercolor='rgba(255, 255, 255, 0)'
                    ),
                    barmode='group',
                    bargap=0.15,  # gap between bars of adjacent location coordinates
                    bargroupgap=0.1,  # gap between bars of the same location coordinate
                    width=800,  # Width of the figure in pixels
                    height=600  # Height of the figure in pixels
                )

                # Display the plot in Streamlit
                st.plotly_chart(fig, use_container_width=True)

            elif plot_option == 'Annual Housing Expense - Buying':

                buying_annual_housing_expenses = [data['Annual Housing Expense'] for data in
                                                  st.session_state.liquid_net_worth.values()]

                buying_liquid_net_worth, down_payment_amount = calculate_buying_liquid_net_worth(
                    st.session_state.home_purchase_price, down_payment_percent, mortgage_interest_rate,
                    mortgage_amortization, annual_home_appreciation, annual_property_tax_percent,
                    initial_annual_maintenance, monthly_utilities, monthly_insurance, monthly_condo_fees,
                    other_monthly_payments, home_sale_costs_percent, lump_sum_fee,
                    st.session_state.general_inflation_rate)

                rental_liquid_net_worth = calculate_rental_liquid_net_worth(st.session_state.home_purchase_costs,
                                                                            st.session_state.down_payment_amount,
                                                                            monthly_rent_payment,
                                                                            annual_rent_increase,
                                                                            monthly_utilities_rental,
                                                                            monthly_renters_insurance,
                                                                            other_monthly_payments_rental,
                                                                            annual_investment_return,
                                                                            buying_annual_housing_expenses)

                crossover_month = None
                crossover_time = None

                # Loop through the years to find the crossover interval
                for year in range(mortgage_amortization - 1):
                    buying_current_year = buying_liquid_net_worth[year]["Liquid Net Worth"]
                    buying_next_year = buying_liquid_net_worth[year + 1]["Liquid Net Worth"]
                    rental_current_year = rental_liquid_net_worth[year]["Liquid Net Worth"]
                    rental_next_year = rental_liquid_net_worth[year + 1]["Liquid Net Worth"]

                    if buying_current_year < rental_current_year and buying_next_year >= rental_next_year:
                        # Interpolate within this year range
                        for month in range(1, 13):  # Check each month
                            fraction_of_year = month / 12.0
                            interpolated_buying = buying_current_year + (
                                        buying_next_year - buying_current_year) * fraction_of_year
                            interpolated_rental = rental_current_year + (
                                        rental_next_year - rental_current_year) * fraction_of_year

                            if interpolated_buying >= interpolated_rental:
                                crossover_month = month
                                crossover_time = year + fraction_of_year
                                break

                        if crossover_month is not None:
                            break

                if crossover_time is not None:
                    st.markdown(f"""
                    <style>
                        .highlight {{
                            font-size: 30px;  /* Font size for the highlighted span */
                            color: red;
                        }}
                        .custom-text {{
                            font-size: 25px;  /* Font size for the entire paragraph */
                        }}
                    </style>
                    <p class='custom-text'>Initially, renting is the better option. After <span class='highlight'>~{crossover_time:.2f} years</span>, buying becomes the better option.</p>
                    """, unsafe_allow_html=True)

                else:
                    st.markdown(f"""
                    <style>
                        .custom-text {{
                            font-size: 25px;  /* Font size for the entire paragraph */
                        }}
                    </style>
                    <p class='custom-text'>No crossover detected within the amortization period.</p>
                    """, unsafe_allow_html=True)

                st.write('\n')
                st.write('\n')

                # Create Buying Scenario Dataframe
                buying_df = pd.DataFrame({
                    "Year": list(range(mortgage_amortization + 1)),
                    "Home Value": [data["Home Value"] for data in buying_liquid_net_worth.values()],
                    "Mortgage Balance": [data["Mortgage Balance"] for data in buying_liquid_net_worth.values()],
                    "Home Equity (Pre-Selling)": [data["Home Equity Pre-Selling"] for data in
                                                  buying_liquid_net_worth.values()],
                    "Selling Costs": [data["Selling Costs"] for data in buying_liquid_net_worth.values()],
                    "Home Equity (Post-Selling)": [data["Home Equity Post-Selling"] for data in
                                                   buying_liquid_net_worth.values()],
                    "Annual Housing Expense": [data["Annual Housing Expense"] for data in
                                               buying_liquid_net_worth.values()],
                    "Monthly Housing Expense": [data["Implied Monthly Housing Expense"] for data in
                                                buying_liquid_net_worth.values()],
                    "Interest Payment": [data["Interest Payment"] for data in buying_liquid_net_worth.values()],
                    "Principal Payment": [data["Principal Payment"] for data in buying_liquid_net_worth.values()],
                    "Liquid Net Worth": [data["Liquid Net Worth"] for data in buying_liquid_net_worth.values()],
                    "Annual Property Tax": [data["Annual Property Tax"] for data in buying_liquid_net_worth.values()],
                    "Annual Maintenance": [data["Annual Maintenance"] for data in buying_liquid_net_worth.values()],
                    "Annual Utilities": [data["Annual Utilities"] for data in buying_liquid_net_worth.values()],
                    "Annual Insurance": [data["Annual Insurance"] for data in buying_liquid_net_worth.values()],
                    "Annual Condo Fees": [data["Annual Condo Fees"] for data in buying_liquid_net_worth.values()],
                    "Annual Other": [data["Annual Other"] for data in buying_liquid_net_worth.values()]
                })

                # Extract data from the dataframes
                years = buying_df['Year']
                buying_mortgage_principal = buying_df['Principal Payment']
                buying_mortgage_interest = buying_df['Interest Payment']
                buying_property_taxes = buying_df['Annual Property Tax']
                buying_maintenance = buying_df['Annual Maintenance']
                buying_utilities = buying_df['Annual Utilities']
                buying_insurance = buying_df['Annual Insurance']
                buying_condo_fees = buying_df['Annual Condo Fees']
                buying_other = buying_df['Annual Other']

                # Buying scenario plot
                fig_buying = go.Figure(data=[
                    go.Bar(name='Mortgage Principal', x=years, y=buying_mortgage_principal),
                    go.Bar(name='Mortgage Interest', x=years, y=buying_mortgage_interest),
                    go.Bar(name='Property Taxes', x=years, y=buying_property_taxes),
                    go.Bar(name='Maintenance', x=years, y=buying_maintenance),
                    go.Bar(name='Utilities', x=years, y=buying_utilities),
                    go.Bar(name='Insurance', x=years, y=buying_insurance),
                    go.Bar(name='Condo Fees', x=years, y=buying_condo_fees),
                    go.Bar(name='Other', x=years, y=buying_other)
                ])

                # Change the bar mode to stack
                fig_buying.update_layout(
                    barmode='stack',
                    title='Buying Annual Expenses Breakdown',
                    xaxis=dict(
                        title='Year',
                        titlefont_size=16,
                        tickfont_size=14),
                    yaxis=dict(
                        title='Annual Housing Expenses ($)',
                        titlefont_size=16,
                        tickfont_size=14,
                    ),
                    legend=dict(
                        x=1.0,
                        y=1.0,
                        bgcolor='rgba(255, 255, 255, 0)',
                        bordercolor='rgba(255, 255, 255, 0)'
                    ),
                    # barmode='group',
                    # bargap=0.15,  # gap between bars of adjacent location coordinates
                    # bargroupgap=0.1,  # gap between bars of the same location coordinate
                    width=1100,  # Width of the figure in pixels
                    height=700  # Height of the figure in pixels
                )

                # Display the plots in Streamlit
                st.plotly_chart(fig_buying)


            elif plot_option == 'Annual Housing Expense - Renting':

                buying_annual_housing_expenses = [data['Annual Housing Expense'] for data in
                                                  st.session_state.liquid_net_worth.values()]

                buying_liquid_net_worth, down_payment_amount = calculate_buying_liquid_net_worth(
                    st.session_state.home_purchase_price, down_payment_percent, mortgage_interest_rate,
                    mortgage_amortization, annual_home_appreciation, annual_property_tax_percent,
                    initial_annual_maintenance, monthly_utilities, monthly_insurance, monthly_condo_fees,
                    other_monthly_payments, home_sale_costs_percent, lump_sum_fee,
                    st.session_state.general_inflation_rate)

                rental_liquid_net_worth = calculate_rental_liquid_net_worth(st.session_state.home_purchase_costs,
                                                                            st.session_state.down_payment_amount,
                                                                            monthly_rent_payment,
                                                                            annual_rent_increase,
                                                                            monthly_utilities_rental,
                                                                            monthly_renters_insurance,
                                                                            other_monthly_payments_rental,
                                                                            annual_investment_return,
                                                                            buying_annual_housing_expenses)

                crossover_month = None
                crossover_time = None

                # Loop through the years to find the crossover interval
                for year in range(mortgage_amortization - 1):
                    buying_current_year = buying_liquid_net_worth[year]["Liquid Net Worth"]
                    buying_next_year = buying_liquid_net_worth[year + 1]["Liquid Net Worth"]
                    rental_current_year = rental_liquid_net_worth[year]["Liquid Net Worth"]
                    rental_next_year = rental_liquid_net_worth[year + 1]["Liquid Net Worth"]

                    if buying_current_year < rental_current_year and buying_next_year >= rental_next_year:
                        # Interpolate within this year range
                        for month in range(1, 13):  # Check each month
                            fraction_of_year = month / 12.0
                            interpolated_buying = buying_current_year + (
                                        buying_next_year - buying_current_year) * fraction_of_year
                            interpolated_rental = rental_current_year + (
                                        rental_next_year - rental_current_year) * fraction_of_year

                            if interpolated_buying >= interpolated_rental:
                                crossover_month = month
                                crossover_time = year + fraction_of_year
                                break

                        if crossover_month is not None:
                            break

                if crossover_time is not None:
                    st.markdown(f"""
                    <style>
                        .highlight {{
                            font-size: 30px;  /* Font size for the highlighted span */
                            color: red;
                        }}
                        .custom-text {{
                            font-size: 25px;  /* Font size for the entire paragraph */
                        }}
                    </style>
                    <p class='custom-text'>Initially, renting is the better option. After <span class='highlight'>~{crossover_time:.2f} years</span>, buying becomes the better option.</p>
                    """, unsafe_allow_html=True)

                else:
                    st.markdown(f"""
                    <style>
                        .custom-text {{
                            font-size: 25px;  /* Font size for the entire paragraph */
                        }}
                    </style>
                    <p class='custom-text'>No crossover detected within the amortization period.</p>
                    """, unsafe_allow_html=True)

                st.write('\n')
                st.write('\n')

                # Create Renting Scenario Dataframe
                renting_df = pd.DataFrame({
                    "Year": list(range(mortgage_amortization + 1)),
                    "Annual Housing Expense Renting": [data["Annual Housing Expense Renting"] for data in
                                                       rental_liquid_net_worth.values()],
                    "BOP Investment Portfolio": [data["BOP Investment Portfolio"] for data in
                                                 rental_liquid_net_worth.values()],
                    "EOP Investment Portfolio": [data["EOP Investment Portfolio"] for data in
                                                 rental_liquid_net_worth.values()],
                    "Liquid Net Worth": [data["Liquid Net Worth"] for data in rental_liquid_net_worth.values()],
                    "Annual Rent Payment": [data["Annual Rent Payment"] for data in rental_liquid_net_worth.values()],
                    "Annual Utilities": [data["Annual Utilities"] for data in rental_liquid_net_worth.values()],
                    "Annual Renters Insurance": [data["Annual Renters Insurance"] for data in
                                                 rental_liquid_net_worth.values()],
                    "Other Annual Fees": [data["Other Annual Fees"] for data in rental_liquid_net_worth.values()]
                })

                # Extract data from the dataframes
                years = renting_df['Year']
                renting_rent = renting_df['Annual Rent Payment']
                renting_utilities = renting_df['Annual Utilities']
                renting_insurance = renting_df['Annual Renters Insurance']
                renting_other = renting_df['Other Annual Fees']

                # Renting scenario plot
                fig_renting = go.Figure(data=[
                    go.Bar(name='Rent', x=years, y=renting_rent),
                    go.Bar(name='Utilities', x=years, y=renting_utilities),
                    go.Bar(name='Insurance', x=years, y=renting_insurance),
                    go.Bar(name='Other Fees', x=years, y=renting_other)
                ])

                # Change the bar mode to stack
                fig_renting.update_layout(
                    barmode='stack',
                    title='Renting Annual Expenses Breakdown',
                    xaxis=dict(
                        title='Year',
                        titlefont_size=16,
                        tickfont_size=14),
                    yaxis=dict(
                        title='Annual Housing Expenses ($)',
                        titlefont_size=16,
                        tickfont_size=14,
                    ),
                    legend=dict(
                        x=1.0,
                        y=1.0,
                        bgcolor='rgba(255, 255, 255, 0)',
                        bordercolor='rgba(255, 255, 255, 0)'
                    ),
                    # barmode='group',
                    # bargap=0.15,  # gap between bars of adjacent location coordinates
                    # bargroupgap=0.1,  # gap between bars of the same location coordinate
                    width=1100,  # Width of the figure in pixels
                    height=700  # Height of the figure in pixels
                )

                # Display the plots in Streamlit
                st.plotly_chart(fig_renting)


            elif plot_option == 'Tables - Calculated Results':

                buying_annual_housing_expenses = [data['Annual Housing Expense'] for data in
                                                  st.session_state.liquid_net_worth.values()]

                buying_liquid_net_worth, down_payment_amount = calculate_buying_liquid_net_worth(
                    st.session_state.home_purchase_price, down_payment_percent, mortgage_interest_rate,
                    mortgage_amortization, annual_home_appreciation, annual_property_tax_percent,
                    initial_annual_maintenance, monthly_utilities, monthly_insurance, monthly_condo_fees,
                    other_monthly_payments, home_sale_costs_percent, lump_sum_fee,
                    st.session_state.general_inflation_rate)

                rental_liquid_net_worth = calculate_rental_liquid_net_worth(st.session_state.home_purchase_costs,
                                                                            st.session_state.down_payment_amount,
                                                                            monthly_rent_payment,
                                                                            annual_rent_increase,
                                                                            monthly_utilities_rental,
                                                                            monthly_renters_insurance,
                                                                            other_monthly_payments_rental,
                                                                            annual_investment_return,
                                                                            buying_annual_housing_expenses)

                crossover_month = None
                crossover_time = None

                # Loop through the years to find the crossover interval
                for year in range(mortgage_amortization - 1):
                    buying_current_year = buying_liquid_net_worth[year]["Liquid Net Worth"]
                    buying_next_year = buying_liquid_net_worth[year + 1]["Liquid Net Worth"]
                    rental_current_year = rental_liquid_net_worth[year]["Liquid Net Worth"]
                    rental_next_year = rental_liquid_net_worth[year + 1]["Liquid Net Worth"]

                    if buying_current_year < rental_current_year and buying_next_year >= rental_next_year:
                        # Interpolate within this year range
                        for month in range(1, 13):  # Check each month
                            fraction_of_year = month / 12.0
                            interpolated_buying = buying_current_year + (
                                        buying_next_year - buying_current_year) * fraction_of_year
                            interpolated_rental = rental_current_year + (
                                        rental_next_year - rental_current_year) * fraction_of_year

                            if interpolated_buying >= interpolated_rental:
                                crossover_month = month
                                crossover_time = year + fraction_of_year
                                break

                        if crossover_month is not None:
                            break

                if crossover_time is not None:
                    st.markdown(f"""
                    <style>
                        .highlight {{
                            font-size: 30px;  /* Font size for the highlighted span */
                            color: red;
                        }}
                        .custom-text {{
                            font-size: 25px;  /* Font size for the entire paragraph */
                        }}
                    </style>
                    <p class='custom-text'>Initially, renting is the better option. After <span class='highlight'>~{crossover_time:.2f} years</span>, buying becomes the better option.</p>
                    """, unsafe_allow_html=True)

                else:
                    st.markdown(f"""
                    <style>
                        .custom-text {{
                            font-size: 25px;  /* Font size for the entire paragraph */
                        }}
                    </style>
                    <p class='custom-text'>No crossover detected within the amortization period.</p>
                    """, unsafe_allow_html=True)

                st.write('\n')
                st.write('\n')

                # Create Buying Scenario Dataframe
                buying_df = pd.DataFrame({
                    "Year": list(range(mortgage_amortization + 1)),
                    "Home Value": [data["Home Value"] for data in buying_liquid_net_worth.values()],
                    "Mortgage Balance": [data["Mortgage Balance"] for data in buying_liquid_net_worth.values()],
                    "Home Equity (Pre-Selling)": [data["Home Equity Pre-Selling"] for data in
                                                  buying_liquid_net_worth.values()],
                    "Selling Costs": [data["Selling Costs"] for data in buying_liquid_net_worth.values()],
                    "Home Equity (Post-Selling)": [data["Home Equity Post-Selling"] for data in
                                                   buying_liquid_net_worth.values()],
                    "Annual Housing Expense": [data["Annual Housing Expense"] for data in
                                               buying_liquid_net_worth.values()],
                    "Monthly Housing Expense": [data["Implied Monthly Housing Expense"] for data in
                                                buying_liquid_net_worth.values()],
                    "Interest Payment": [data["Interest Payment"] for data in buying_liquid_net_worth.values()],
                    "Principal Payment": [data["Principal Payment"] for data in buying_liquid_net_worth.values()],
                    "Liquid Net Worth": [data["Liquid Net Worth"] for data in buying_liquid_net_worth.values()],
                    "Annual Property Tax": [data["Annual Property Tax"] for data in buying_liquid_net_worth.values()],
                    "Annual Maintenance": [data["Annual Maintenance"] for data in buying_liquid_net_worth.values()],
                    "Annual Utilities": [data["Annual Utilities"] for data in buying_liquid_net_worth.values()],
                    "Annual Insurance": [data["Annual Insurance"] for data in buying_liquid_net_worth.values()],
                    "Annual Condo Fees": [data["Annual Condo Fees"] for data in buying_liquid_net_worth.values()],
                    "Annual Other": [data["Annual Other"] for data in buying_liquid_net_worth.values()]
                })

                # Create Renting Scenario Dataframe
                renting_df = pd.DataFrame({
                    "Year": list(range(mortgage_amortization + 1)),
                    "Annual Housing Expense Renting": [data["Annual Housing Expense Renting"] for data in
                                                       rental_liquid_net_worth.values()],
                    "BOP Investment Portfolio": [data["BOP Investment Portfolio"] for data in
                                                 rental_liquid_net_worth.values()],
                    "EOP Investment Portfolio": [data["EOP Investment Portfolio"] for data in
                                                 rental_liquid_net_worth.values()],
                    "Liquid Net Worth": [data["Liquid Net Worth"] for data in rental_liquid_net_worth.values()],
                    "Annual Rent Payment": [data["Annual Rent Payment"] for data in rental_liquid_net_worth.values()],
                    "Annual Utilities": [data["Annual Utilities"] for data in rental_liquid_net_worth.values()],
                    "Annual Renters Insurance": [data["Annual Renters Insurance"] for data in
                                                 rental_liquid_net_worth.values()],
                    "Other Annual Fees": [data["Other Annual Fees"] for data in rental_liquid_net_worth.values()]
                })

                # Create and style the DataFrame
                buying_heatmap_columns = ['Home Value', 'Mortgage Balance', 'Liquid Net Worth']
                renting_heatmap_columns = ['Liquid Net Worth']

                styled_buying_df = buying_df.style.background_gradient(cmap='coolwarm', subset=buying_heatmap_columns)
                styled_renting_df = renting_df.style.background_gradient(cmap='coolwarm',
                                                                         subset=renting_heatmap_columns)

                # Display styled DataFrame in Streamlit
                st.dataframe(styled_buying_df)
                st.dataframe(styled_renting_df)

        # with col4:
        #     st.write("This column is half the size of 2 and 3")


    if __name__ == "__main__":
        main()

# Content for Tab 3
with tab3:
    ####### CHANGE COLOR TAB ################

    # Define your custom styles using CSS
    custom_css_tab3 = """
        <style>
            /* You can use .st-ck to target the multiselect widget container */
            .st-ck { 
                background-color: #00695C; /* Dark background for better contrast */
            }
            /* Use .st-bq to target the multiselect widget options */
            .st-bq {
                color: #FFAB40; /* White text color for better contrast */
            }
        </style>
    """

    # Inject custom CSS with markdown
    st.markdown(custom_css_tab3, unsafe_allow_html=True)

    ######## CHANGE COLOR TEXT BOX SELECTION ###########

    # Custom CSS to inject via markdown
    custom_css = """
        <style>
            /* Target the multiselect widget's text */
            .Select-multi-value-wrapper .Select-value-label {
                color: ##F9FBE7; /* Replace with your desired hex color code */
            }
            /* You may also need to change the color of the placeholder text */
            .Select-placeholder {
                color: ##F9FBE7; /* Replace with your desired hex color code */
            }
        </style>
    """

    # Inject custom CSS with markdown
    st.markdown(custom_css, unsafe_allow_html=True)

    # Write your custom CSS
    custom_css_text = """
        <style>
            /* Target the container of the selected options */
            .css-12jo7m5 {
                color: #000000; /* Change to desired text color, e.g., black */
            }

            /* Target the specific labels of the selected options */
            .css-tlfecz-indicatorContainer {
                color: #000000; /* Change to desired text color, e.g., black */
            }

            /* You may also need to adjust the color when hovering */
            .css-12jo7m5:hover {
                color: #000000; /* Change to desired text color, e.g., black */
            }
        </style>
    """

    # Inject the custom CSS into the Streamlit app
    st.markdown(custom_css_text, unsafe_allow_html=True)

    st.markdown('<h2 style="color: #FFFDE7;">Community Valuation Trends</h2>', unsafe_allow_html=True)

    st.markdown(
        "Zoom into the real estate landscape with 'Community Valuation Trends', where you can compare the average assessed property values across communities over time. Dive in, select various neighborhoods, and witness the average price evolution on an intuitive map.")
    st.write(" ")

    # import data
    df = pd.read_pickle('Grouped_Data_ALL-Years.pkl')
    se_df = pd.read_csv('merged_df_property_prices.csv')
    gdf = gpd.read_file('gdf_comm_districts.geojson')
    gdf_projected = gdf.to_crs(epsg=32612)  # corresponds to UTM Zone 12N

    # Streamlit widget for multi-selection
    selected_communities = st.multiselect(
        'Select Communities',
        options=df['COMM_NAME'].unique(),
        # default=df['COMM_NAME'].unique()  # Default to all communities
        default=[df['COMM_NAME'].unique()[0]]  # Default to the first community

    )
    # Filter the DataFrame and GeoDataFrame based on selected communities
    filtered_df = df[df['COMM_NAME'].isin(selected_communities)]
    gdf['is_selected'] = gdf['NAME'].isin(selected_communities)

    # Create the Plotly plot for the selected communities
    fig = px.line(filtered_df, x='ROLL_YEAR', y='ASSESSED_VALUE', color='COMM_NAME',
                  labels={'ROLL_YEAR': 'Year', 'ASSESSED_VALUE': 'Average Assessed Value', 'COMM_NAME': 'Community'},
                  title='Average Assessed Value per Community Over Years')
    fig.update_layout(title_text="Assessed Value", title_x=0.3, width=800, height=600)

    # st.plotly_chart(fig)
    fig1 = px.choropleth_mapbox(gdf, geojson=gdf.geometry.__geo_interface__,
                                locations=gdf.index,
                                color='is_selected',
                                center={"lat": gdf.geometry.centroid.y.mean(), "lon": gdf.geometry.centroid.x.mean()},
                                mapbox_style="stamen-toner",
                                zoom=9,
                                hover_name='NAME',
                                color_discrete_map={True: "yellow", False: "gray"})
    fig1.update_layout(title_text="Community Map", title_x=0.3, width=800, height=600)

    # Create columns for side by side layout
    col1, col2 = st.columns([1, 1])

    # Use columns to display figures
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        # Check if the filtered GeoDataFrame is not empty
        if not gdf.empty:
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.write("No communities selected or community data not available.")

    ####################
    st.markdown('### Social Economic Factors')

    # Streamlit widget for multi-selection
    selected_variables = st.multiselect(
        'Select Factors',
        options=se_df.columns[1:],  # All column names excluding 'year_month'
        default=se_df.columns[1]  # Default to the first variable
    )

    # Create a Plotly figure
    fig2 = go.Figure()

    # Add traces for selected variables
    for variable in selected_variables:
        fig2.add_trace(go.Scatter(x=se_df['year_month'], y=se_df[variable], name=variable))

    # Update layout
    fig2.update_layout(
        title_text="Selected Variables Over Time",
        xaxis_title="Year-Month",
        yaxis_title="Value",
        width=1600,  # Width of the figure in pixels
        height=600  # Height of the figure in pixels
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig2)

    ####################
    # Create a subplot figure
    fig3 = make_subplots(rows=3, cols=2, specs=[[{'secondary_y': True}, {'secondary_y': True}],
                                                [{'secondary_y': True}, {'secondary_y': True}],
                                                [{'secondary_y': True}, {'secondary_y': True}], ],
                         subplot_titles=['Employment and Unemployment', 'Consumer Price Index', 'BCPI', 'Net migration',
                                         'Construction and WTI', '5 year Mortgage rate vs house price'])

    # Employment and Unemployment
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Employment'], name='Employment'), row=1, col=1,
                   secondary_y=False)
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Labour force'], name='Labour force'), row=1, col=1,
                   secondary_y=False)
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Full-time employment'], name='Full-time Employment'),
                   row=1, col=1, secondary_y=False)
    # fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Part-time employment'], name='Part-time Employment'), row=1, col=1)
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Unemployment'], name='Unemployment'), row=1, col=1,
                   secondary_y=True)
    fig3.update_yaxes(title_text="Employment", secondary_y=False, row=1, col=1)
    fig3.update_yaxes(title_text="Unemployment", secondary_y=True, row=1, col=1)

    # # Employment Rate and Unemployment Rate
    # fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Employment rate'], name='Employment Rate'), row=1, col=2, secondary_y=False)
    # fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Unemployment rate'], name='Unemployment Rate'), row=1, col=2, secondary_y=True)
    # fig3.update_yaxes(title_text="Employment rate", secondary_y=False, row=1, col=2)
    # fig3.update_yaxes(title_text="Unemployment rate", secondary_y=True, row=1, col=2)

    # BCPI Variables
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Annual_BCPI_Total'], name='Annual_BCPI_Total'), row=2,
                   col=1)
    fig3.add_trace(
        go.Scatter(x=se_df['year_month'], y=se_df['Annual_BCPI_Excluding_Energy'], name='Annual_BCPI_Excluding_Energy'),
        row=2, col=1)
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Annual_BCPI_Energy'], name='Annual_BCPI_Energy'), row=2,
                   col=1)
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Annual_BCPI_Metals_and_Minerals'],
                              name='Annual_BCPI_Metals_and_Minerals'), row=2, col=1)
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Annual_BCPI_Forestry'], name='Annual_BCPI_Forestry'),
                   row=2, col=1)
    fig3.add_trace(
        go.Scatter(x=se_df['year_month'], y=se_df['Annual_BCPI_Agriculture'], name='Annual_BCPI_Agriculture'), row=2,
        col=1)
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Annual_BCPI_Fish'], name='Annual_BCPI_Fish'), row=2,
                   col=1)

    # CPI Variables
    # fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Total_CPI'], name='Total_CPI'), row=2, col=2)
    # fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Total_CPI_seasonally_adjusted'], name='Total_CPI_seasonally_adjusted'), row=2, col=2)
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['CPI_trim'], name='CPI_trim'), row=1, col=2)
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['CPI_median'], name='CPI_median'), row=1, col=2)
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['CPI_common'], name='CPI_common'), row=1, col=2)

    # Population
    # fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Population'], name='Population'), row=3, col=1, secondary_y=False)
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['net_migration'], name='Net_migration'), row=2, col=2,
                   secondary_y=False)
    # Update y-axis titles
    # fig3.update_yaxes(title_text="Population", secondary_y=False, row=3, col=1)
    # fig3.update_yaxes(title_text="Net migration", secondary_y=True, row=3, col=1)

    # Construction WTI
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['housing_starts'], name='Housing Starts'), row=3, col=2,
                   secondary_y=False)
    # 'WTI' on the secondary y-axis
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['WTI'], name='WTI'), row=3, col=2, secondary_y=True)
    # Update y-axis titles
    fig3.update_yaxes(title_text="Housing Starts", secondary_y=False, row=3, col=2)
    fig3.update_yaxes(title_text="WTI", secondary_y=True, row=3, col=2)

    # House price and mortagge rate
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['Home_Prices_Calgary'], name='Home_Prices_Calgary'), row=3,
                   col=1, secondary_y=False)
    fig3.add_trace(go.Scatter(x=se_df['year_month'], y=se_df['5_year_mortgage_rate'], name='5_year_mortgage_rate'),
                   row=3, col=1, secondary_y=True)
    # Update y-axis titles
    fig3.update_yaxes(title_text="Home_Prices_Calgary", secondary_y=False, row=3, col=1)
    fig3.update_yaxes(title_text="5_year_mortgage_rate", secondary_y=True, row=3, col=1)

    # Update layout
    fig3.update_layout(height=1000, width=1600, title_text="Time Series Analysis")
    # fig3.show()

    # Display the figure
    st.plotly_chart(fig3)

# Content for Tab 4
with tab4:
    import streamlit as st
    import pandas as pd
    import os, sys
    import numpy as np
    import warnings

    warnings.filterwarnings('ignore')
    import folium
    from folium.plugins import *
    import geocoder
    import geopandas as gpd
    import branca.colormap as cm
    from streamlit_folium import folium_static
    from pandas.api.types import (
        is_categorical_dtype,
        is_datetime64_any_dtype,
        is_numeric_dtype,
        is_object_dtype,
    )

    if "estimated_home_price" in st.session_state:
        # Retrieve and assign to a variable
        estimated_home_price_tab4 = st.session_state['estimated_home_price']

        # Now you can use this variable as needed
        st.write(f"Estimated Home Price from Financial Fit Finder Tab: ${estimated_home_price_tab4:,.2f}")
        # Other operations using estimated_home_price_tab4
    else:
        st.write("Estimated home price is not calculated yet. Please go to Financial Fit Finder Tab.")
        estimated_home_price_tab4 = 500000
        # price_predict = estimated_home_price_tab4


    def create_map(comms, comms_sub):
        x_map = comms.centroid.x.mean()
        y_map = comms.centroid.y.mean()
        colormap = cm.linear.YlGnBu_09.to_step(data=comms_sub['COMM_SLT'], method='quant',
                                               quantiles=[0, 0.1, 0.75, 0.9, 0.98, 1])

        m = folium.Map(location=[y_map, x_map], zoom_start=10, tiles=None)
        folium.TileLayer('CartoDB positron', name="Light Map", control=False).add_to(m)
        colormap.caption = "# of Affordable Residental Properties in Calgary Communities"
        style_function = lambda x: {"weight": 0.5,
                                    'color': 'black',
                                    'fillColor': colormap(x['properties']['COMM_SLT']),
                                    'fillOpacity': 0.75}
        highlight_function = lambda x: {'fillColor': '#000000',
                                        'color': '#000000',
                                        'fillOpacity': 0.5,
                                        'weight': 0.1}
        RES = folium.features.GeoJson(
            comms_sub,
            style_function=style_function,
            control=False,
            highlight_function=highlight_function,
            tooltip=folium.features.GeoJsonTooltip(fields=['COMMUNITY_NAME', 'PROP', 'COMM_SLT'],
                                                   aliases=['Community: ',
                                                            'Proportion of affordable residences for YOU: ',
                                                            'Number of affordable residences for YOU: '],
                                                   style=(
                                                       "background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"),
                                                   sticky=True
                                                   )
        )
        colormap.add_to(m)
        m.add_child(RES)
        return m


    def get_properties(sub, comms, max_price, low_end):
        sub = sub[((sub['VALUE_2023'] >= low_end) & (sub['VALUE_2023'] <= max_price)) &
                  ((sub['VALUE_2024'] >= low_end) & (sub['VALUE_2024'] <= max_price)) &
                  ((sub['VALUE_2025'] >= low_end) & (sub['VALUE_2025'] <= max_price)) &
                  ((sub['VALUE_2026'] >= low_end) & (sub['VALUE_2026'] <= max_price))
                  ]
        sub['COMM_SLT'] = sub.groupby(['COMMUNITY_NAME'])['PROPERTY_ID'].transform('nunique')
        sub = round(sub, 3)
        sub['PROP'] = round(sub['COMM_SLT'] / sub['COMM_ALL'], 3)

        sub_trunc = sub[['COMMUNITY_NAME', 'COMM_ALL', 'COMM_SLT', 'PROP']].drop_duplicates()

        # comms = comms[['name', 'geometry']].rename(columns={'name': 'COMMUNITY_NAME'})
        comms_sub = comms.merge(sub_trunc, on="COMMUNITY_NAME", how='left')
        comms_sub = comms_sub.fillna(0)
        map = create_map(comms, comms_sub)
        return sub, map


    def dataframe_with_selections(df):
        df_with_selections = df.copy()
        df_with_selections.insert(0, "Select", False)
        # Get dataframe row-selections from user with st.data_editor
        edited_df = st.data_editor(df_with_selections, hide_index=True,
                                   column_config={"Select": st.column_config.CheckboxColumn(required=True)},
                                   disabled=df.columns,
                                   )
        # Filter the dataframe using the temporary column, then drop the column
        selected_rows = edited_df[edited_df.Select]
        return selected_rows.drop('Select', axis=1)


    def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds a UI on top of a dataframe to let viewers filter columns
        """
        modify = st.checkbox("Add filters")
        if not modify:
            return df
        df = df.copy()

        modification_container = st.container()

        with modification_container:
            to_filter_columns = st.multiselect("Filter results on", df.columns)
            for column in to_filter_columns:
                left, right = st.columns((1, 20))
                # Treat columns with < 10 unique values as categorical
                if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                    user_cat_input = right.multiselect(f"Values for {column}", df[column].unique(),
                                                       default=list(df[column].unique()), )
                    df = df[df[column].isin(user_cat_input)]
                elif is_numeric_dtype(df[column]):
                    _min = int(df[column].min())
                    _max = int(df[column].max())
                    step = int((_max - _min) / 100)
                    user_num_input = right.slider(f"Values for {column}", min_value=_min, max_value=_max,
                                                  value=(_min, _max), step=step, )
                    df = df[df[column].between(*user_num_input)]
                else:
                    user_text_input = right.text_input(f"Enter value for {column}", )
                    if user_text_input:
                        df = df[df[column].astype(str).str.contains(user_text_input.upper())]
        return df


    def property_map(mini_df, sub, comms):
        if (len(mini_df) > 0) & (len(mini_df) < 25):
            data_point = list(mini_df.COMMUNITY_NAME.unique())
            x_val = comms[comms['COMMUNITY_NAME'].isin(data_point)].centroid.x.mean()
            y_val = comms[comms['COMMUNITY_NAME'].isin(data_point)].centroid.y.mean()

            m2 = folium.Map(location=[y_val, x_val], zoom_start=12)
            folium.TileLayer('openstreetmap').add_to(m2)
            folium.LayerControl().add_to(m2)
            formatter = "function(num) {return L.Util.formatNum(num,3) + ' ° ';};"
            MousePosition(
                position='topright',
                separator=' | ',
                empty_string='NaN',
                lng_first=True,
                num_digits=20,
                prefix='Coordinates:',
                lat_formatter=formatter,
                lng_formatter=formatter
            ).add_to(m2)
            for i in range(len(mini_df)):
                folium.Marker(location=[mini_df.iloc[i]["LATITUDE"], mini_df.iloc[i]["LONGITUDE"]],
                              popup='ADDRESS: ' + mini_df.iloc[i]['ADDRESS'] + ', CURRENT VALUE: $' + str(
                                  mini_df.iloc[i]['VALUE_2023']),
                              icon=folium.Icon(color='blue')
                              ).add_to(m2)
            return m2
        else:
            m2 = folium.Map(location=[51.049999, -114.066666], zoom_start=10)
            folium.TileLayer('CartoDB positron', name="Light Map").add_to(m2)
            folium.LayerControl().add_to(m2)
            formatter = "function(num) {return L.Util.formatNum(num,3) + ' ° ';};"
            MousePosition(
                position='topright',
                separator=' | ',
                empty_string='NaN',
                lng_first=True,
                num_digits=20,
                prefix='Coordinates:',
                lat_formatter=formatter,
                lng_formatter=formatter
            ).add_to(m2)
            return m2


    properties = pd.read_csv('Calgary Property Data.csv')
    properties = properties.rename(columns={'COMM_NAME': 'COMMUNITY_NAME'})
    communities = gpd.read_file(
        'geo_export_439b7cc6-4dd0-4905-af0d-7c9d5901f392.shp')
    communities = communities[['name', 'geometry']].rename(columns={'name': 'COMMUNITY_NAME'})

    col1, col2, col3 = st.columns([2, 4, 2])

    with col1.container():
        st.write("")
    with col2.container():

        st.markdown('<h4 style="color: #FFFDE7;">Calgary Custom Affordability Map</h4>', unsafe_allow_html=True)
        st.markdown(
            "Unveil personalized affordable housing counts with 'Calgary's Custom Affordability Map'. Each community's data reflects properties within your budget, guiding you to your ideal locale.")
        st.write(" ")

        price_predict = estimated_home_price_tab4
        # price_predict = st.number_input('Home Purchase Price', min_value=0.0, value=500000.0, step=10000.0,
        #                                 format='%.2f',
        #                                 help='Enter your maximum home purchase price')
        low_end = price_predict * 0.75
        property_list, map = get_properties(properties, communities, price_predict, low_end)
        property_list = property_list.reset_index(drop=True)
        # folium_static(map)
        map.fit_bounds(map.get_bounds())  # This ensures that the map is centered and zoomed appropriately
        folium_static(map, width=1200, height=700)  # Adjust the width and height as necessary
    with col3.container():
        st.write("")

    col4, col5, col6, col7 = st.columns([1, 0.05, 1, 0.2])

    with col4.container():
        st.markdown('<h4 style="color: #FFFDE7;">Select & Explore Properties</h4>', unsafe_allow_html=True)
        st.write(" \n\n")
        selection = dataframe_with_selections(filter_dataframe(property_list[['ADDRESS', 'COMMUNITY_NAME', 'VALUE_2023',
                                                                              'VALUE_2024', 'VALUE_2025', 'VALUE_2026',
                                                                              'LATITUDE', 'LONGITUDE']]))
    with col5.container():
        st.write("")

    with col6.container():
        st.markdown('<h4 style="color: #FFFDE7;">Property Details</h4>', unsafe_allow_html=True)
        st.markdown(
            "Utilize the 'Select & Explore' feature to interactively choose specific locations on the Calgary map. This tool empowers you to focus on communities of interest and discover available properties tailored to your preferences.")
        st.write(" ")
        folium_static(property_map(selection, property_list, communities), width=1000, height=400)

    with col7.container():
        st.write("")

