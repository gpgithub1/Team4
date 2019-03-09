var config = {
    apiKey: "AIzaSyCU87yhweJP3j2Y4DvPMgPZT-0ouAflB80",
    authDomain: "capstoneteam4-bb4ce.firebaseapp.com",
    databaseURL: "https://capstoneteam4-bb4ce.firebaseio.com",
    projectId: "capstoneteam4-bb4ce",
    storageBucket: "capstoneteam4-bb4ce.appspot.com",
    messagingSenderId: "110799787101"
  };
  firebase.initializeApp(config);

var travelRef = firebase.database().ref('TravelCustomers');

document.getElementById('registerForm').addEventListener('submit', submitForm);

function submitForm(e) {
	e.preventDefault();

	var username = getInput('username');
	var password = getInput('password');
	var pass2 = getInput('pass2');
	var firstName = getInput('firstName');
	var lastName = getInput('lastName');
	var email = getInput('email');
	var phone = getInput('phone');
	var street = getInput('street');
	var city = getInput('city');
	var state = getInput('state');
	var zip = getInput('zip');

	//Only thing code is missing is a way to check if the username is already taken. 

	if(password == pass2) {
		saveTravel(username, password, firstName, lastName, email, phone, street, city, state, zip);
		document.getElementById('registerForm').reset();
	}
	

}

function getInput(id) {
	return document.getElementById(id).value;
}

function saveTravel(username, password, firstName, lastName, email, phone, street, city, state, zip) {
	var newTravelRef = travelRef.push();
	newTravelRef.set({
		username:username,
		password:password,
		firstName:firstName,
		lastName:lastName,
		email:email,
		phone:phone,
		street:street,
		city:city,
		state:state,
		zip:zip
	});
}

function match() {
  if (getInput('password') == getInput('pass2')) {
    document.getElementById('matching').style.color = 'green';
    document.getElementById('matching').innerHTML = 'Passwords Match';
  } else {
    document.getElementById('matching').style.color = 'red';
    document.getElementById('matching').innerHTML = 'Passwords do not match';
  }
}
