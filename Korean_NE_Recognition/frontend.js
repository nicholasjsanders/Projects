function enable(sender) { 
	if(document.getElementById('annotated').checked){
	  document.getElementById("person").removeAttribute('disabled');
	  document.getElementById("organization").removeAttribute('disabled');
	  document.getElementById("place").removeAttribute('disabled');
	}
	else{
	  document.getElementById("person").disabled = true;
	  document.getElementById("organization").disabled = true;
	  document.getElementById("place").disabled = true;
	}
  }

function update_page(response) {
	var div = document.getElementById("maintext");
	div.innerHTML = response;

}

function submit_form () {   
	var form = document.getElementById("form");         
	var formData = new FormData(form);
	var searchParams = new URLSearchParams(formData);
	var queryString = searchParams.toString();
	xmlHttpRqst = new XMLHttpRequest( )
	xmlHttpRqst.onload = function(e) {update_page(xmlHttpRqst.response);} 
	xmlHttpRqst.open( "GET", "/?" + queryString);
	xmlHttpRqst.send();

}


