This is a simple Flask booking app containerized by Docker. It is to simulate a patient's experience when booking for a doctor's appointment. There are 5 scenarios in this app:
1. Patient makes a booking
2. Patient cancels a booking
3. Doctor cancels a booking
4. Doctor inputs details of consultation into booking records
5. Patient makes payment for the consultation



This application requires the following to run:

1. Install and run WampServer
2. Create a new user account called "is213" with no password in phpMyadmin. This account needs to have all the privileges classified under "Data, Structures and Administration" (e.g select, insert etc)
3. Load all included sql files found in the "data" folder

To run the solution:
1. open cmd and navigate to the "program" folder directory
2. run docker-compose build
3. run docker-compose up
4. To test how the microservices react with the UIs, go to the "UI" folder and double click the html file to open the UI for a specific scenario.
Note: The UIs are not linked so they need to be opened separately for each user scenario.


Detailed instructions for each scenario

For scenario 1:
1. Enter the username in the input field
2. Click "Make a booking" on a specific timing
Note: a sample username is in the default database "danielben"

For scenario 2:
1. Enter the booking id in the input field
2. Click the "Search" button
3. Click "Cancel booking"
Note: a sample booking id in the default database is "1"

For scenario 3:
1. Enter the doctor id in the input field
2. Click the "Search" button
3. Select one of the bookings using the radio button
4. Click "Cancel booking"
Note: a sample doctor id in the default database is "501" or "502"

For scenario 4:
1. Enter the doctor id in the input field
2. Click the "Search" button
3. To add a prescription, add a booking id that corresponds to the doctor, choose the drugs and quantity and click the "Add prescription" button
4. To update consultation details, a booking id that corresponds to the doctor, type the consultation details and click the Update consultation details" button
Note: a sample doctor id is in the default database "501" or "502"

For scenario 5:
1. Enter the patient id in the input field
2. Click the "Search" button
3. Click the "Pay" button
4. Click the "Paypal checkout" button
5. For the email and password, use the sample paypal account below
Note: a sample patient id in the default database is "801"


To complete the transaction process in scenario 5, the following patient account should be used.

Patient Account
username: G2T6-Patient1@ESD.com
password: Patient@G2T6

To see the transaction log received by business users, the following sandbox account can be used.

Business Account
username: sb-v7s3b5761440@personal.example.com
password: nM3>}9C: