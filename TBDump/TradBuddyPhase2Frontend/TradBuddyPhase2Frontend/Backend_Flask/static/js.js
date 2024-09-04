
function handleChildAccountOption(accountId) {
    // Get the ul element corresponding to the clicked account
    var accountOptions = document.getElementById("accountOptions" + accountId);

    // Toggle the visibility of the child options
    if (accountOptions.classList.contains("hidden")) {
        accountOptions.classList.remove("hidden");

    } else {
        accountOptions.classList.add("hidden");
    }
}





