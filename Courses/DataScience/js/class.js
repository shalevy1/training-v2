var STAGE = "{{STAGE}}";
var API_BASE_URL = "{{API_BASE_URL}}";

function getClassCertificate() {
  var id_token = Cookies.get("com.neo4j.accounts.idToken");
  return $.ajax
  ({
    type: "POST",
    url: API_BASE_URL + "/genClassCertificate",
    contentType: "application/json",
    dataType: 'json',
    async: true,
    data: JSON.stringify(
      { "className": window.trainingClassName
      }),
    headers: {
      "Authorization": id_token
    }
  });
}

function getEnrollmentForClass() {
  var id_token = Cookies.get("com.neo4j.accounts.idToken");
  return $.ajax
  ({
    type: "GET",
    url: API_BASE_URL + "/getClassEnrollment?className=" + window.trainingClassName,
    async: true,
    headers: {
      "Authorization": id_token
    }
  });
}

function enrollStudentInClass(firstName, lastName) {
  var id_token = Cookies.get("com.neo4j.accounts.idToken");
  return $.ajax
  ({
    type: "POST",
    url: API_BASE_URL + "/setClassEnrollment",
    contentType: "application/json",
    dataType: 'json',
    async: true,
    data: JSON.stringify(
      { "className": window.trainingClassName,
        "firstName": firstName,
        "lastName": lastName
      }),
    headers: {
      "Authorization": id_token
    }
  });
}

function logTrainingView() {
  var id_token = Cookies.get("com.neo4j.accounts.idToken");
  return $.ajax
  ({
    type: "POST",
    url: API_BASE_URL + "/logTrainingView",
    contentType: "application/json",
    dataType: 'json',
    async: true,
    data: JSON.stringify(
      { "className": window.trainingClassName,
        "partName": window.trainingPartName || 'uknown'
      }),
    headers: {
      "Authorization": id_token
    }
  });
}

jQuery(document).ready(function () {
  if (Cookies.get("com.neo4j.accounts.idToken")) { 
    // we're authenticated
    // could check expiration of token, but not critical for this app
    // still need to check quiz status
    /*
    logTrainingView().then(
      function() {
        return getQuizStatus();
      }
    );
    */
  } else if (typeof window.trainingPartName !== 'undefined') {
    window.location = "https://neo4j.com/accounts/login/?targetUrl=" + encodeURI(window.location.href);
  }
});
