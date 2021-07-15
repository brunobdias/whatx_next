function sendEmail(contactForm) {

    let templateParams = {
      from_name: contactForm.name.value,
      from_email: contactForm.email.value,
      message: contactForm.comment.value
    };
  
    emailjs
      .send("service_qrmt_whatxNext", "template_vf90o8b", templateParams)
      .then(
        function (response) {
          //Credit to https://stackoverflow.com/questions/6653556/jquery-javascript-function-to-clear-all-the-fields-of-a-form
          $("#contactForm").trigger("reset");
          //End Credit
          window.location.href = '/email_sent/';
        },
        function (error) {
          alert("FAILED...", error);
          console.log("FAILED...", error);
        }
      );
  
    return false;
  }