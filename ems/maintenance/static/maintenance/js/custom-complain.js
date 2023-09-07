var data;
function getMachineDetails(){  
    let equipmentSelect = document.querySelector('#machine-select');    
    let equipmentId = equipmentSelect.value;

    if (equipmentId){
        fetch("/get_machines/?equipment_id=" + equipmentId)
            .then(function(response){
                if (response.ok){
                    return response.json();
                }
                else{
                    throw new Error('Network Error')
                }
            }).then(function(result){
                data = result;
                populateMachineDetails();
            })
            .catch(function(error){
                console.error("There was a problem with the fetch operaion", error);
            });
    }
    else{


        alert('The selected equipment does not have any related machines')
    }
}

function populateMachineDetails(){

    let machineSelect = document.querySelector('#machine-num-select');
    if(machineSelect.childNodes.length > 0){
        removeChild(machineSelect)
    }
    let optionsList = [];
    
    data.machine_options.forEach(function(option){

        let machineOptionElem = document.createElement('option');
        machineOptionElem.value = option.id;
        machineOptionElem.textContent = option.name;
        optionsList.push(machineOptionElem);
    
    });
    
    machineSelect.append(...optionsList);
    machineSelect.disabled = false;

}

function onMachineSelectChange(){
    let machineSelect = document.querySelector('#machine-num-select');
    let selectMachineId = machineSelect.value;
    populateMalfunctionPartList(data, selectMachineId);

}

function populateMalfunctionPartList(data, selectMachineId){
    let malfunctionPart = document.querySelector('#malfunction-part');
    if (malfunctionPart.childNodes.length > 0){
        removeChild(malfunctionPart)    
    }
    let optionsList = []


    data.machine_options.forEach(function(option){
        if(option.id === Number(selectMachineId)){
            Array.from(malfunctionPart.children).forEach( (option) => {
                if (option.textContent === 'Select a Machine Number'){
                    option.remove();
                }
            }); 
                option.spares.forEach(function(spare){
                var malfunctionPartOption = document.createElement('option');
                malfunctionPartOption.value = spare.id;
                malfunctionPartOption.textContent = spare.name;
                optionsList.push(malfunctionPartOption)
            
            })
        }
    });
    malfunctionPart.append(...optionsList)
    malfunctionPart.disabled = false;

}

function removeChild(id){
    // console.log("Inside remove method")
    while(id.firstChild){
        id.removeChild(id.firstChild)
    }
}


function getCurrentDateTime(){
    var now = new Date();
    var datetime = now.toISOString().substring(0, 16)
    document.getElementById('date-time').value = datetime
}


