'use strict';
window.addEventListener('load', function () {
  document.getElementById('sign-out').onclick = function() {
    firebase.auth().signOut();
  };
  document.getElementById('sign-in').onclick = function() {
    var ui = new firebaseui.auth.AuthUI(firebase.auth());
    ui.start('#firebase-auth-container', uiConfig);
  };
  document.getElementById('home').onclick = function() {
    return redirect("/");
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

    document.getElementById('sign-in').hidden = true;
    document.getElementById('addcar').hidden = false;
    console.log('Signed in as ${user.displayName} (${user.email})');
    user.getIdToken().then(function(token) {
      document.cookie = "token=" + token;
    });
  } else {
    document.getElementById('sign-out').hidden = true;
    document.getElementById('login-info').hidden = true;
    document.getElementById('sign-in').hidden = false;
    document.getElementById('addcar').hidden = true;
    document.cookie = "token=";
  }
  }, function(error) {
    console.log(error);
    alert('Unable to log in: ' + error);
  });
});
