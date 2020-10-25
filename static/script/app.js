const signInForm = document.querySelector(".sign-in__form");
const signInInputs = document.querySelectorAll(".sign-in__form input");
const signInBtn = document.querySelector(".sign-in__form button");

const nameField = document.querySelector("#username");
const emailField = document.querySelector("input[type='email']");
const pwdField = document.querySelector("input[type='password']");
const confirmPwdField = document.querySelector("#confirmpass");

const signUpForm = document.querySelector(".sign-up__form");
const signUpInputs = document.querySelectorAll(".sign-up__form input");
const signUpBtn = document.querySelector(".sign-up__form button");

function toggleButtonDisable(form, inputs, btn) {
  for (let i = 0; i < inputs.length; i++) {
    inputs[i].addEventListener("keyup", (e) => {
      console.log("key");
      if (form == signUpForm) {
        if (
          nameField.value != "" &&
          emailField.value != "" &&
          pwdField.value != "" &&
          confirmPwdField.value != ""
        ) {
          btn.disabled = false;
        } else {
          btn.disabled = true;
        }
      } else if (form == signInForm) {
        if (emailField.value != "" && pwdField.value != "") {
          btn.disabled = false;
        } else {
          btn.disabled = true;
        }
      }
    });
  }
}

if (signUpForm) {
  toggleButtonDisable(signUpForm, signUpInputs, signUpBtn);
}
if (signInForm) {
  toggleButtonDisable(signInForm, signInInputs, signInBtn);
}

// Add to Cart action
const addToCartBtn = document.querySelector(".addToCartBtn");
if (addToCartBtn) {
    addToCartBtn.addEventListener("click", showDialog);
}

// Add To Cart Model
const overlay = document.getElementById("overlay");
const dialog = document.getElementById("dialog");
const closeBtns = document.querySelectorAll("#dialog .cancel");
const productDetail = document.querySelector("product-details-section");

function showDialog(e) {
  e.preventDefault();
  overlay.style.display = "block";
  dialog.style.display = "block";
  productDetail.style.opacity = 0.1; 
}
function hideDialog() {
  overlay.style.display = "none";
  dialog.style.display = "none";
  productDetail.style.opacity = 1; 

}
if (overlay) {
  overlay.addEventListener("click", hideDialog);
}
if (dialog) {
  for (let i = 0; i < closeBtns.length; i++) {
    closeBtns[i].addEventListener("click", hideDialog);
  }
}

alerts = document.querySelectorAll(".alert");

if(alerts){
    setTimeout(()=>{
        for (let i = 0; i < alerts.length; i++) {
            alerts[i].style.display = "none";
            
        }
    }, 3000);
};