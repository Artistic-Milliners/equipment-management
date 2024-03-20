// var data;

// function machine_num(){
//     let machineNum = document.querySelector('#machine-num-select')
//     let selectMachineId = machineNum.value
//     console.log(machineNum.value)
//     if (machineNum) {
//         populateMalfunctionPartList(data, selectMachineId);
//     }
// }

// function getMachineDetails(){  
//     let equipmentSelect = document.querySelector('#machine-select');    
//     let equipmentId = equipmentSelect.value;

//     if (equipmentId){
//         fetch("/get_machines/?equipment_id=" + equipmentId)
//             .then(function(response){
//                 if (response.ok){
//                     return response.json();
//                 }
//                 else{
//                     throw new Error('Network Error')
//                 }
//             }).then(function(result){
//                 data = result;
//                 populateMachineDetails();
//             })
//             .catch(function(error){
//                 console.error("There was a problem with the fetch operaion", error);
//             });
//     }
//     else{
//         alert('The selected equipment does not have any related machines')
//     }
// }

// function populateMachineDetails(){

//     let machineSelect = document.querySelector('#machine-num-select');
//     if(machineSelect.childNodes.length > 0){
//         removeChild(machineSelect)
//     }
//     let optionsList = [];
    
//     data.machine_options.forEach(function(option){

//         let machineOptionElem = document.createElement('option');
//         machineOptionElem.value = option.id;
//         machineOptionElem.textContent = option.name;
//         optionsList.push(machineOptionElem);
    
//     });
    
//     machineSelect.append(...optionsList);
//     machineSelect.disabled = false;

// }

// function onMachineSelectChange(){
//     let machineSelect = document.querySelector('#machine-num-select');
//     let selectMachineId = machineSelect.value;
//     populateMalfunctionPartList(data, selectMachineId);

// }



// function populateMalfunctionPartList(data, selectMachineId){
//     let malfunctionPart = document.querySelector('#malfunction-part');
//     console.log("I am inside malfunctino")
//     if (malfunctionPart.childNodes.length > 0){
//         removeChild(malfunctionPart)    
//     }
//     let optionsList = []


//     data.machine_options.forEach(function(option){
//         if(option.id === Number(selectMachineId)){
//             Array.from(malfunctionPart.children).forEach( (option) => {
//                 if (option.textContent === 'Select a Machine Number'){
//                     option.remove();
//                 }
//             }); 
//                 option.spares.forEach(function(spare){
//                 var malfunctionPartOption = document.createElement('option');
//                 malfunctionPartOption.value = spare.id;
//                 malfunctionPartOption.textContent = spare.name+" "+spare.item_code;
//                 optionsList.push(malfunctionPartOption)
            
//             })
//         }
//     });
//     malfunctionPart.append(...optionsList)
//     malfunctionPart.disabled = false;

// }

// function removeChild(id){
//     // console.log("Inside remove method")
//     while(id.firstChild){
//         id.removeChild(id.firstChild)
//     }
// }


// function getCurrentDateTime(){
//     var now = new Date();
//     var datetime = now.toISOString().substring(0, 16);
//     document.getElementById('date-time').value = datetime;
// }


function searchSpare(malfunctionId, searchId){
    var text = document.getElementById(searchId).value;
    console.log(text)
    Array.from(document.getElementById(malfunctionId).children).forEach((option) => {
        if (!option.textContent.toLowerCase().includes(text)){
            option.style.display = 'none';
            // console.log(option.textContent);
        }
        else{
            option.style.display = 'block'
            console.log(option)
        }
    })
    

}

let slideIndex = 1;
showSlides(slideIndex);

// Next/previous controls
function plusSlides(n) {
  showSlides(slideIndex += n);
}

// Thumbnail image controls
function currentSlide(n) {
  showSlides(slideIndex = n);
}

function showSlides(n) {
  let i;
  let slides = document.getElementsByClassName("mySlides");
  let dots = document.getElementsByClassName("dot");
  if (n > slides.length) {slideIndex = 1}
  if (n < 1) {slideIndex = slides.length}
  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
  }
  for (i = 0; i < dots.length; i++) {
    dots[i].className = dots[i].className.replace(" active", "");
  }
  slides[slideIndex-1].style.display = "block";
  dots[slideIndex-1].className += " active";
}


