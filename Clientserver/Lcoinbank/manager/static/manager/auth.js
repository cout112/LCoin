



document.addEventListener('DOMContentLoaded', () =>  {


	document.querySelector("body").style.backgroundColor="#ffe6cc";
	



	//On index.html
	if(document.querySelector("#indexpage")){
		//let columnheight = window.innerHeight - 400;
		//document.querySelector('#accountsrow').style.height = `${columnheight}px`;

		document.querySelector('#formnewaccount').style.display = 'none';
		document.querySelector("#formsendcoin").style.display = 'none';
		console.log(document.querySelector("#formsendcoin").style.display);






		document.addEventListener('click', event=>{


			let button = event.target;


			if (button.id == 'new_account' && document.querySelector("#formnewaccount").style.display == 'none'){
				document.querySelector("#formnewaccount").style.display = '';
			} else if (button.id == 'new_account' && document.querySelector("#formnewaccount").style.display == '') {
				document.querySelector("#formnewaccount").style.display = 'none';
			}

			if (button.id == 'sendcoin' && document.querySelector("#formsendcoin").style.display == 'none'){
				document.querySelector("#formsendcoin").style.display = '';
			} else if (button.id == 'sendcoin' && document.querySelector("#formsendcoin").style.display == ''){
				document.querySelector("#formsendcoin").style.display = 'none';
			}

		})


	}








	//On authenticate.html
	if (document.querySelector("#cardsignup")){
			document.querySelector("#cardsignup").style.display="none";
			

			document.querySelector("#signup").disabled = true;
		
		






		document.addEventListener('keyup', event=>{

			if (document.querySelector("#usernamesignup").value != '' && 
				document.querySelector("#emailsignup").value != '' &&
				document.querySelector("#password1signup").value != '' &&
				document.querySelector("#password2signup").value != '' && 
				document.querySelector("#password1signup").value == document.querySelector("#password2signup").value){

				document.querySelector("#signup").disabled = false;

			} else {

				document.querySelector("#signup").disabled = true;

			}

			if (document.querySelector("#password1signup").value != '' &&
				document.querySelector("#password2signup").value != '' && 
				document.querySelector("#password1signup").value != document.querySelector("#password2signup").value){
				document.querySelector("#passwordfail").innerHTML = 'Password doesn\'t match';
			} else {
				document.querySelector("#passwordfail").innerHTML = '';
			}



			

		})

		document.addEventListener('click', event => {
			target = event.target;
			if (target.id == "tosignup"){
				document.querySelector("#cardsignup").style.display="";
				document.querySelector("#cardlogin").style.display="none";
				document.querySelector("#tosignup").style.display="none";

			}

		})

	}







})