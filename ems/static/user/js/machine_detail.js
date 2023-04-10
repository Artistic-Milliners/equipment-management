function modalData(formid){

console.log(formid)
var form = document.getElementById(formid)
var url = form.dataset.url ;

form.addEventListener("submit", function(e){
e.preventDefault();

const formData = new FormData(form);

console.log(formData)

// formData.append('csrfmiddlewaretoken', '{{ csrf_token }}');
for (var pair of formData.entries()) {
    console.log(pair[0]+ ', ' + pair[1]); 
}

fetch(url, {
method: 'POST',
body: formData
})
.then(response => response.json())
.then(data => {
console.log('Success:', data);

})
.catch(error => {
console.error('Error:', error);
});
});


}



