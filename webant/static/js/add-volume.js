function autoSelectLanguage() {
    document.getElementById('language').value = navigator.language.substr(0,2)
}

window.onload = function() {
    autoSelectLanguage()
}
