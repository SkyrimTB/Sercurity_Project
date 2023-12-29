//Check if the password and confirm_password is match
var check = function() {
    if (document.getElementById('password').value ==
      document.getElementById('confirm_password').value) {
      document.getElementById('check_message').style.color = 'green';
      document.getElementById('check_message').innerHTML = 'Matching';
    } else {
      document.getElementById('check_message').style.color = 'red';
      document.getElementById('check_message').innerHTML = 'Not Matching';
    }
  }

//Check if the password and confirm_password is match
document.getElementById("register").addEventListener("click", function()  {  

    if(document.getElementById('password').value != document.getElementById('confirm_password').value)  
    {   
      alert("Passwords did not match");
    }

    //Save the secret key to the localStorage
    var username = document.getElementById('username').value;
    localStorage.setItem(username, document.getElementById('user_private_key_id').value);
    
  }  );

