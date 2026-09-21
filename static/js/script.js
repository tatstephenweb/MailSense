loadEmails('all') // Load all emails on page load

function refreshPage() {
  location.reload();
}

function openDetailView() {
    document.getElementById('list-view').classList.add('hidden');
    document.getElementById('detail-view').classList.remove('hidden');
    document.getElementById('detail-view').classList.add('flex');
}

function closeDetailView() {
    document.getElementById('detail-view').classList.add('hidden');
    document.getElementById('list-view').classList.remove('hidden');
}

// Function to fetch emails based on priority
async function loadEmails(priority) {
    try {
        const response = await fetch(`/emails?priority=${priority}`);
        
        const data = await response.json();
        
        let priorityTitle = document.getElementById('list-priority-title')
        priorityTitle.innerHTML = priority + " priority"

        // Render the emails in the frontend
        renderEmails(data.emails);
        //renderDetail(data.emails);

    }   
    catch (error) {
            console.error('Error fetching emails:', error);
        }
    closeSidebar() 
}

async function showMailDetail(emailId) {
    try {
        const response = await fetch(`/emails/${emailId}`);
        const data= await response.json();

        console.log(data)
        renderDetail(data.emails[0])
        openDetailView();
        //renderDetail(data.email);
    }
    catch (error) {
        console.error('Error fetching email detail:', error);
    }
}


function renderEmails(emails) {
    const container = document.getElementById('mail-list');
    container.innerHTML = '';

    emails.forEach(email => {
      let emailAddress = `${email.sender}`;
      const firstLetter = emailAddress.charAt(0).toUpperCase();
      
      let priority = `${email.priority}`;
      let key = priority.toLowerCase();
      let select = priorityColors[key];
      
      const div = document.createElement('button');
        div.type = 'button';
        div.className = `mail-row w-full flex gap-4 border-b border-ink/10 px-2 md:px-3 py-2.5 text-left`;
        
        //TO ADD CLICK FUNCTION TO THE BUTTON TO OPEN THE DETAILS OF THE MAIL
        div.addEventListener('click', () => {
            showMailDetail(email.id);
        });
        
        // CREATE THE CONTENTS OF THE BUTTON MAIL LIST
        
        div.innerHTML = `
          <div class="avatar-email h-10 w-10 rounded-full flex items-center justify-center text-20px font-bold shrink-0">
            ${firstLetter}
          </div>
          <div class="flex flex-col w-full min-w-0 root">
            <div class="min-w-0 truncate text-[14px] mail-row_sender">${email.sender}</div>
            
            <div class="flex w-full items-center justify-between gap-2 bg-blue">
              <span class="truncate min-w-0 flex-1 text-[14px] mail-row_subject">${email.subject}</span>
              <span class="mail-row_priority text-center shrink-0">${email.priority}</span>
            </div>
            
            <div class="min-w-0 truncate text-[12px] mail-row_snippet">${email.snippet}</div>
          </div>
          `;
        let avatarDiv = div.querySelector('.avatar-email');
        if (colors[firstLetter]) {
            avatarDiv.style.backgroundColor = colors[firstLetter];
        } else {
            avatarDiv.style.backgroundColor = '#bdc3c7'; // default color if no match
        }
        container.appendChild(div);

        let priorityBadge = div.querySelector(".mail-row_priority");
      
        if (priority == "high"){
          priorityBadge.innerHTML = priority;
          priorityBadge.style.background = select.bg;
          priorityBadge.style.color = select.text;
        } else if(priority == "medium"){
          priorityBadge.innerHTML = priority;
          priorityBadge.style.background = select.bg;
          priorityBadge.style.color = select.text;
        }else{
          priorityBadge.innerHTML = priority;
          priorityBadge.style.background = select.bg;
          priorityBadge.style.color = select.text;
        }
    });
}

// set colors for each first letter of the email address
const colors = {
    A: "#e74c3c", B: "#3498db", C: "#2ecc71", D: "#f1c40f",
    E: "#9b59b6", F: "#1abc9c", G: "#e67e22", H: "#34495e",
    I: "#16a085", J: "#c0392b", K: "#2980b9", L: "#27ae60",
    M: "#f39c12", N: "#8e44ad", O: "#d35400", P: "#7f8c8d",
    Q: "#2c3e50", R: "#e84393", S: "#00b894", T: "#0984e3",
    U: "#6c5ce7", V: "#fd79a8", W: "#fdcb6e", X: "#00cec9",
    Y: "#636e72", Z: "#b2bec3"
  };

const priorityColors = {
  high:   { bg: "#ffecea", text: "#c00202" },
  medium: { bg: "#fef7d9", text: "#cbba00" },
  low:    { bg: "#e4ffef", text: "#00ac1d" }
};


function renderDetail(email) {
    let mailDetail= document.getElementById('mail-detail');
    let emailAddress = `${email.sender}`;
    const firstLetter = emailAddress.charAt(0).toUpperCase();
    
    mailDetail.innerHTML = `
        <div class="view-fade max-w-2xl">

          <h2 class="text-[24px] font-bold tracking-tight mb-7 mt-10">${email.subject}</h2>
          <div class="flex items-center gap-3 pb-5 mb-6 border-b border-border">
            <div class="avatar-email-detail text-15px p-5">
              ${firstLetter}
            </div>

            <div class="flex justify-between w-full">
              <div class="min-w-0">
                <p class="text-[15px] font-medium">${email.sender}</p>
                <p class="text-[12px]">${email.recieved_at}</p>
              </div>
              
              <p class="text-[12px]">${email.priority}</p>
            </div>

          </div>
          <p class="text-[15px] leading-7 whitespace-pre-line break-words">${email.snippet}</p>
        </div>
      `

      let avatarDiv = document.querySelector('.avatar-email-detail');
        if (colors[firstLetter]) {
            avatarDiv.style.backgroundColor = colors[firstLetter];
        } else {
            avatarDiv.style.backgroundColor = '#bdc3c7'; // default color if no match
        }
    
}

let sidebar= document.getElementById('sidebar')
let backdrop = document.getElementById('sidebar-backdrop')
let openSidebarBtn= document.getElementById('open-sidebar')
let closeSidebarBtn= document.getElementById('close-sidebar')

let sideNav = document.getElementById('side-nav')

function openSidebar() {
   sidebar.classList.remove('-translate-x-full');
    backdrop.classList.remove('hidden');
  }

  function closeSidebar() {
    sidebar.classList.add('-translate-x-full');
    backdrop.classList.add('hidden');
  }

openSidebarBtn.addEventListener('click', openSidebar);
closeSidebarBtn.addEventListener('click', closeSidebar);
backdrop.addEventListener('click', closeSidebar);


