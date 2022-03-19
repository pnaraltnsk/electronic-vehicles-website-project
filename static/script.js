'use strict';
window.addEventListener('load', function () {
  document.getElementById('sign-out').onclick = function() {
  // ask firebase to sign out the user
    firebase.auth().signOut();
  };
  document.getElementById('home').onclick = function() {
  // ask firebase to sign out the user
    redirect("/");
  };
  var uiConfig = {
    signInSuccessUrl: '/',
    signInOptions: [
      firebase.auth.EmailAuthProvider.PROVIDER_ID
    ]
 };
 firebase.auth().onAuthStateChanged(function(user) {
  if(user) {
    document.getElementById('sign-out').hidden = false;
    document.getElementById('home').hidden = false;
    document.getElementById('login-info').hidden = false;
    //document.getElementById('sign-in').hidden = true;
    console.log('Signed in as ${user.displayName} (${user.email})');
    user.getIdToken().then(function(token) {
      document.cookie = "token=" + token;
    });
  } else {
    var ui = new firebaseui.auth.AuthUI(firebase.auth());
    ui.start('#firebase-auth-container', uiConfig);
    document.getElementById('sign-out').hidden = true;
    document.getElementById('home').hidden = true;
    document.getElementById('login-info').hidden = true;
    //document.getElementById('sign-in').hidden = false;
    document.cookie = "token=";
  }
  }, function(error) {
    console.log(error);
    alert('Unable to log in: ' + error);
  });
});
