function decodeEntities(s) {
  const t = document.createElement('textarea');
  t.innerHTML = s ?? '';
  return t.value;
}
function clean(s) {
  return decodeEntities(String(s ?? '')).replace(/[&<>"']/g, c =>
    ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

let currentFilter = 'all';
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

// SERVICE WORKER FOR THE PUSH NOTIFICATIONS
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js')
    .then(reg => console.log('Service worker registered:', reg))
    .catch(err => console.error('Service worker registration failed:', err));
}

const VAPID_PUBLIC_KEY = "BMRGOGQqpot4FDlnw3qH9cCYhvU7w7yktwg4yCOCJ2hlqnrwq11tQoRqzuEUAkmDNVihyRjhOqcuFEjtXwfMgbg";

function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = atob(base64);
    return Uint8Array.from([...rawData].map(char => char.charCodeAt(0)));
}

async function subscribeToPush() {
    const permission = await Notification.requestPermission();
    if (permission !== 'granted') {
        console.log('Notification permission denied');
        return;
    }

    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
    });

    await fetch('/api/save-subscription', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(subscription)
    });

    console.log('Subscribed and saved:', subscription);
}

subscribeToPush();

// Function to fetch emails based on priority
async function loadEmails(priority) {
  currentFilter = priority;

  document.querySelectorAll('.filter-btn').forEach(btn => {
      btn.classList.remove('nav-item--active');
  });
  document.querySelector(`.filter-btn[data-filter="${priority}"]`).classList.add('nav-item--active');


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
      //let select = priorityColors[key];
      let select = priorityColors[key] || priorityColors.medium;
      
      const div = document.createElement('button');
        div.type = 'button';
        div.className = `mail-row w-full flex gap-4 border-b border-ink/10 px-2 md:px-3 py-2.5 text-left`;
        div.dataset.emailId = email.id;
        
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
            <div class="min-w-0 truncate text-[14px] mail-row_sender">${clean(email.sender)}</div>
            
            <div class="flex w-full items-center justify-between gap-2 bg-blue">
              <span class="truncate min-w-0 flex-1 text-[14px] mail-row_subject">${clean(email.subject)}</span>
              <span class="mail-row_priority text-center shrink-0">${email.priority}</span>
            </div>
            
            <div class="min-w-0 truncate text-[12px] mail-row_snippet">${clean(email.snippet)}</div>
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

function stylePrioritySelect(selectEl, priority) {
  const c = priorityColors[String(priority).toLowerCase()] || priorityColors.medium;
  selectEl.style.background = c.bg;
  selectEl.style.color = c.text;
}


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

              <select 
                id="priority-select" 
                data-email-id="${email.id}"
                class="bg-[#FFF] text-sm rounded px-2 focus:outline-none">
                <option value="High" ${email.priority === 'High' ? 'selected' : ''}>High</option>
                <option value="Medium" ${email.priority === 'Medium' ? 'selected' : ''}>Medium</option>
                <option value="Low" ${email.priority === 'Low' ? 'selected' : ''}>Low</option>
              </select>
            </div>

          </div>
          <p class="text-[15px] leading-7 whitespace-pre-line break-words">${email.snippet}</p>
        </div>
      `

      let avatarDiv = document.querySelector('.avatar-email-detail');
        if (colors[firstLetter]) {
            avatarDiv.style.backgroundColor = colors[firstLetter];
        } else {
            avatarDiv.style.backgroundColor = '#bdc3c7';
        }

      // NEW: wire up the dropdown now that it's actually in the DOM
      let prioritySelect = document.getElementById('priority-select');
      stylePrioritySelect(prioritySelect, email.priority);   // colour on first load

      prioritySelect.addEventListener('change', function() {
        stylePrioritySelect(this, this.value);               // colour changes when user picks
        updateEmailPriority(this.dataset.emailId, this.value);
      });
}

function updateEmailPriority(emailId, newPriority) {
  fetch(`/emails/${emailId}/priority`, {
    method: 'PATCH',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({priority: newPriority})
  })
  .then(res => res.json())
  .then(data => {
    if (!data.success) return;

    // find this email's row in the list, if it's currently rendered
    const row = document.querySelector(`[data-email-id="${emailId}"]`);
    if (!row) return;

    // if a specific filter is active and this email no longer matches it, drop the row
    if (currentFilter !== 'all' && currentFilter !== newPriority) {
      row.remove();
      return;
    }

    const badge = row.querySelector('.mail-row_priority');
    const colorSet = priorityColors[newPriority.toLowerCase()];

    badge.innerHTML = newPriority;
    badge.style.background = colorSet.bg;
    badge.style.color = colorSet.text;
  });
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


//load profile data when user clicks on the profile button.
const btn = document.getElementById("profile-btn");
const popover = document.getElementById("profile-popover");
let loaded = false;

async function loadProfile() {
  const res = await fetch("/api/me");
  if (!res.ok) return;
  const user = await res.json();

  document.getElementById("profile-name").textContent = user.name;
  document.getElementById("profile-email").textContent = user.email;
  document.getElementById("profile-joined").textContent =
    new Date((user.created_at || "").replace(" ", "T")).toLocaleDateString(
      undefined, { year: "numeric", month: "long", day: "numeric" }
    );

  const pic = document.getElementById("profile-pic");
  const letter = document.getElementById("profile-letter");
  letter.textContent = (user.name || user.email || "?")[0].toUpperCase();

  const showLetter = () => {
    pic.classList.add("hidden");
    letter.classList.remove("hidden");
    letter.classList.add("flex");
  };
  if (user.picture_url) {
    pic.onerror = showLetter;
    pic.src = user.picture_url;
  } else {
    showLetter();
  }
  loaded = true;
}

function positionPopover() {
  const rect = btn.getBoundingClientRect();
  const pop = popover.getBoundingClientRect();
  const gap = 8;

  let left = rect.right + gap;          // to the right of the button
  let top = rect.top;                   // lined up with the button

  if (left + pop.width > window.innerWidth) {      // no room on the right
    left = Math.max(gap, rect.left - pop.width - gap);
  }
  if (top + pop.height > window.innerHeight - gap) {   // no room below
    top = window.innerHeight - pop.height - gap;
  }
  popover.style.left = left + "px";
  popover.style.top = top + "px";
}

btn.addEventListener("click", async (e) => {
  e.stopPropagation();
  if (!popover.classList.contains("hidden")) {
    popover.classList.add("hidden");
    return;
  }
  popover.classList.remove("hidden");
  if (!loaded) await loadProfile();
  positionPopover();
});

document.addEventListener("click", (e) => {
  if (!popover.contains(e.target)) popover.classList.add("hidden");
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") popover.classList.add("hidden");
});
window.addEventListener("resize", () => {
  if (!popover.classList.contains("hidden")) positionPopover();
});

async function logout() {
  const reg = await navigator.serviceWorker.ready;
  const sub = await reg.pushManager.getSubscription();
  if (sub) {
    await fetch('/push/unsubscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ endpoint: sub.endpoint })
    });
    await sub.unsubscribe();
  }
  window.location.href = '/logout';
}