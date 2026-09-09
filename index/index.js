let message = document.getElementById("show info")

let today = new Date();
const options ={month:'long', day:'numeric'}
const formattedDate = today.toLocaleDateString('en-US', options);

const todaysDate= document.getElementById("today-date")
todaysDate.textContent = formattedDate

let myTodos =[]
const inputText = document.getElementById("task-input")
const addTaskBtn = document.getElementById("add-task-btn")
let ulEl = document.getElementById("task-list-el")


addTaskBtn.addEventListener("click", function(){
    message.textContent = "Task Added!"
    setTimeout(() => { message.textContent = ""; }, 5000);

    myTodos.push(inputText.value)
    inputText.value = ""
    render(myTodos)
})


function render(todos){
    let listItems =" "
    for(let i=0; i<todos.length; i++){

        listItems += `
        <li id="task-list-single-el">
            <label>
                <input type="checkbox" id="checkbox-el">
            </label>
            
            <span id="task-text-el">${todos[i]} </span>
            <span><button type="button" id="clearBtn" aria-label="Clear text">&times;</button></span>
        </li>
        ` 

        ulEl.innerHTML = listItems
    }
  
}




















function openSidebar(){
    document.querySelector('body').classList.add("open")
}

function closeSidebar(){
    document.querySelector('body').classList.remove("open")
}