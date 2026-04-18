// --- INITIAL LOAD ---
document.addEventListener('DOMContentLoaded', () => {
    // Check path to render appropriate dashboard data
    if (window.location.pathname.includes('student.html')) {
        renderStudentStatus();
    }
    if (window.location.pathname.includes('parent.html')) {
        renderParentDashboard();
    }
    if (window.location.pathname.includes('warden.html')) {
        renderWardenDashboard();
    }
});

// --- LOGIN ROUTING ---
if (document.getElementById('loginForm')) {
    document.getElementById('loginForm').addEventListener('submit', (e) => {
        e.preventDefault();
        const role = document.getElementById('userRole').value;
        const pass = document.getElementById('password').value;

        if (pass === "123") {
            localStorage.setItem('currentUser', role);
            window.location.href = role + ".html";
        } else {
            alert("Incorrect password!");
        }
    });
}

// --- STUDENT SUBMISSION ---
if (document.getElementById('leaveForm')) {
    document.getElementById('leaveForm').addEventListener('submit', (e) => {
        e.preventDefault();
        
        const app = {
            id: Date.now(),
            name: document.getElementById('stuName').value,
            roll: document.getElementById('rollNo').value,
            room: document.getElementById('roomNo').value,
            mobile: document.getElementById('stuMobile').value,
            parentMobile: document.getElementById('parentMobile').value,
            reason: document.getElementById('reason').value,
            dates: document.getElementById('sDate').value + " to " + document.getElementById('eDate').value,
            parentStatus: 'Pending',
            wardenStatus: 'Pending'
        };

        let db = JSON.parse(localStorage.getItem('leave_records')) || [];
        db.push(app);
        localStorage.setItem('leave_records', JSON.stringify(db));
        
        alert("Success: Leave request submitted and sent to Parent.");
        e.target.reset();
        renderStudentStatus(); // Refresh table immediately
    });
}

// --- STUDENT STATUS RENDER ---
function renderStudentStatus() {
    const list = document.getElementById('studentStatusList');
    if (!list) return;
    const db = JSON.parse(localStorage.getItem('leave_records')) || [];
    
    list.innerHTML = db.map(r => {
        let wStatusHtml = r.wardenStatus === 'Issued' 
            ? '<span style="color:green; font-weight:bold;">Gatepass Issued ✅</span>' 
            : '<span style="color:orange;">Awaiting Warden</span>';
            
        let pStatusHtml = r.parentStatus === 'Approved' 
            ? '<span style="color:green; font-weight:bold;">Approved</span>' 
            : '<span style="color:orange;">Pending</span>';

        return `
            <tr>
                <td style="padding:12px; border:1px solid #ddd;">${r.room}</td>
                <td style="padding:12px; border:1px solid #ddd;">${r.reason}</td>
                <td style="padding:12px; border:1px solid #ddd;">${pStatusHtml}</td>
                <td style="padding:12px; border:1px solid #ddd;">${wStatusHtml}</td>
            </tr>
        `;
    }).reverse().join('') || "<tr><td colspan='4' style='text-align:center; padding:20px;'>No leave records.</td></tr>";
}

// --- PARENT DASHBOARD RENDER ---
function renderParentDashboard() {
    const table = document.getElementById('parentList');
    if (!table) return;
    const db = JSON.parse(localStorage.getItem('leave_records')) || [];
    
    table.innerHTML = db.filter(r => r.parentStatus === 'Pending').map(r => `
        <tr>
            <td>${r.name}</td>
            <td>${r.reason}</td>
            <td>${r.dates}</td>
            <td><button class="btn-nmims-submit" style="padding:8px 15px; font-size:0.8rem;" onclick="updateRecord(${r.id}, 'parentStatus', 'Approved')">APPROVE</button></td>
        </tr>`).join('') || "<tr><td colspan='4' style='text-align:center; padding:20px;'>No pending requests to approve.</td></tr>";
}

// --- WARDEN DASHBOARD RENDER ---
function renderWardenDashboard() {
    const table = document.getElementById('wardenList');
    if (!table) return;
    const db = JSON.parse(localStorage.getItem('leave_records')) || [];
    
    table.innerHTML = db.filter(r => r.parentStatus === 'Approved' && r.wardenStatus === 'Pending').map(r => `
        <tr>
            <td>${r.name} (Room: ${r.room})</td>
            <td><span style="color:green; font-weight:bold;">Verified (Mob: ${r.parentMobile})</span></td>
            <td><button class="btn-nmims-submit" style="padding:8px 15px; font-size:0.8rem; background:green;" onclick="updateRecord(${r.id}, 'wardenStatus', 'Issued')">ISSUE GATEPASS</button></td>
        </tr>`).join('') || "<tr><td colspan='3' style='text-align:center; padding:20px;'>Waiting for parent verifications...</td></tr>";
}

// --- CORE UTILITIES ---
function updateRecord(id, field, value) {
    let db = JSON.parse(localStorage.getItem('leave_records'));
    let idx = db.findIndex(r => r.id === id);
    if (idx !== -1) {
        db[idx][field] = value;
        localStorage.setItem('leave_records', JSON.stringify(db));
        location.reload();
    }
}

function logout() {
    localStorage.removeItem('currentUser');
    window.location.href = 'index.html';
}