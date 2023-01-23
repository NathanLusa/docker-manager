console.log('Temo na área tiozão')

var action_list = document.querySelectorAll('.docker-event');

for (const item in action_list) {
    if (action_list.hasOwnProperty(item)) {
      const btn_action = action_list[item];
      const content = document.getElementById("content");
      const exec_cmd = document.getElementById("exec-cmd");
      
      btn_action.addEventListener("click", function(event){
        event.preventDefault(); 
          
        
        var url = btn_action.getAttribute('data-url')
        url += '&command=' + exec_cmd.value
        
        content.innerHTML = url + '\n';
        
        fetch(url)
            .then(response => response.json())
            .then(data => {content.innerHTML += data.message});
        //  .then(response => response.text())
        //  .then(data => {content.innerHTML += data});
    })

    };
};
