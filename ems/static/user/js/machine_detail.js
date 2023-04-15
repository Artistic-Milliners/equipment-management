function modalData(formid){



var form = document.getElementById(formid)
var url = form.dataset.url ;

console.log(url)

form.addEventListener("submit", function(e){
e.preventDefault();

const formData = new FormData(form);



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

function updateModal(btn){

    var itemCode = btn.getAttribute("data-item-code");
    var itemName = btn.getAttribute("data-name");
    var itemQuantity = btn.getAttribute("data-quantity");
    var itemUnit = btn.getAttribute("data-unit");
    var itemUrl = btn.getAttribute("data-url");

    document.getElementById("update-item-code").value = itemCode;
    document.getElementById("update-name").value = itemName;
    document.getElementById("update-quantity").value = itemQuantity;
    document.getElementById("update-unit").value = itemUnit;
    
    document.getElementById("update-form").setAttribute("data-url", itemUrl);

}

function issueModal(btn){

    var  itemCode = btn.getAttribute("data-item-code");
    var  name = btn.getAttribute("data-name");
    var  quantity = btn.getAttribute("data-quantity");
    var  unit = btn.getAttribute("data-unit");
    var url = btn.getAttribute("data-url");
    
    document.getElementById("issue-item-code").value = itemCode;
    document.getElementById("issue-name").value = name;
    document.getElementById("issue-quantity").value = quantity;
    document.getElementById("issue-unit").value = unit;

    console.log(url)
    document.getElementById("issuance-form").setAttribute("data-url", url);
    
}
s



