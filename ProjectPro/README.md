# README and VIDEO

# Accessibility:
- Big buttons and text
- Contrasting bold colours
- Labels on all input fields for forms

# Additional Features:

Recent transaction history displaying the last 5 transactions.
- When the user has logged into their account, I iterate through all the completed transactions to do with them and get the last 5 transactions from the database. The last 5 will be the 5 most recent transactions,

Ability to split bill unevenly using a share percentage that has to add up to 100 percent.
- I have added the ability to unevenly share the bill using percentages. I have implemented an error check to make sure the percentages add up to 100. I get all the percentages from the form of all the payers and calculate how much of the total they have to pay.

Flash messages of when someone has completed a bill.
- Along with having flash messages for when someone sends a new bill, I also have flash messages for when someone has paid their portion of the bill. I have an attribute in my "Share" class called "senderEmail" which is the email of the person that sent the bill. I terate through all the people that need to pay a bill from the "Share" class and see if the logged in user sent any bills. For all the bills the logged in user has sent off, I check to see if any of them are completed using the "complete" boolean attribute. For all completed bills, I check to see if the user knows if they are completed or not using the "dateTime" function and the boolean attribute "checkPaid". If the time the bill was sent was before the user last logged in and "checkPaid" is False, I flash a new message of someone comoleting their bill.

Adding multiple housemates and certain members to split bills differently with.
- Following up on the dynamic percentages point, I also have the ability to keep adding multiple housemates to the same bill in one go. I used JQuery's HTML.append() function to keep adding rows of the form when the user clicks "add housemate". The tricky bit was to keep the title of the bill fixed on what the user picked for the first housemate so that they all get charged for the same bill. Furthermore, it was important to keep the total the same so that all the money calculations are consistent. I managed to do both these things. In my "cwk.py" file, I had to use "getlist()" for all the form input fields as now I was potentially dealing with multiple entries. Moreover, I had to "zip()" the contents of the form so that I get all the data from all the fields person by person instead of category by category. This is how I executed this feature.

Used Ajax for the update and delete button and to add housemates.
- My final additional feature was using Ajax for the "Update" and "Delete" buttons. For both functions in my ".js" file, I used the "$.post()" method to send off the relevant data to my Flask file instead of having to refresh the page for the flask file to get the new information. To actually make the changes, I simply get the ID of the parts I am dealing with and update their HTML using JQuery.