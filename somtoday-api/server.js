const express = require('express');
const cors = require('cors');
const somtoday = require('somtoday.js').default;
const path = require('path');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 3000;

app.use(cors());
app.use(express.static(path.join(__dirname, 'public')));

let currentUser = null;
let loginError = null;

// Initialize somtoday login automatically
async function initSomtoday() {
    try {
        console.log(`Zoeken naar school: ${process.env.SCHOOL}`);
        const org = await somtoday.searchOrganisation({
            name: process.env.SCHOOL,
        });

        if (!org) {
            loginError = 'School niet gevonden. Controleer het SCHOOL veld in .env';
            console.error(loginError);
            return;
        }

        console.log(`Inloggen met gebruiker: ${process.env.USERNAME}`);
        currentUser = await org.authenticate({
            username: process.env.USERNAME,
            password: process.env.PASSWORD,
        });

        console.log('Succesvol ingelogd bij Somtoday!');
    } catch (error) {
        loginError = `Fout bij inloggen: ${error.message}`;
        console.error(loginError);
    }
}

// Call init on startup if variables are set
if (process.env.SCHOOL && process.env.USERNAME && process.env.PASSWORD) {
    initSomtoday();
}

// API endpoint to check status
app.get('/api/status', (req, res) => {
    if (currentUser) {
        res.json({ status: 'connected', message: 'Verbonden met Somtoday!' });
    } else if (loginError) {
        res.status(500).json({ status: 'error', message: loginError });
    } else {
        res.json({ status: 'waiting', message: 'Nog niet ingelogd of inloggegevens ontbreken in .env' });
    }
});

// API endpoint to fetch schedule
app.get('/api/rooster', async (req, res) => {
    if (!currentUser) return res.status(401).json({ error: 'Niet ingelogd bij Somtoday.' });

    try {
        const today = new Date();
        const nextWeek = new Date(today);
        nextWeek.setDate(today.getDate() + 7);

        // Somtoday.js uses AppointmentManager
        const appointmentsManager = currentUser.appointmentsManager;

        // Fetch appointments for next 7 days
        const appointmentsCollection = await appointmentsManager.fetch({
            startDate: today,
            endDate: nextWeek
        });

        // Format the output to be simple for AI / UI
        const rooster = Array.from(appointmentsCollection.values()).map(appt => ({
            id: appt.id,
            vak: appt.abbreviation,
            titel: appt.title,
            startTijd: appt.startValidity,
            eindTijd: appt.endValidity,
            locatie: appt.locations ? appt.locations.map(l => l.name).join(', ') : '',
            docent: appt.teachers ? appt.teachers.map(t => t.abbreviation).join(', ') : '',
            lesuur: appt.appointmentType ? appt.appointmentType.description : ''
        }));

        res.json({ rooster });
    } catch (error) {
        console.error('Fout bij ophalen rooster:', error);
        res.status(500).json({ error: 'Fout bij het ophalen van het rooster.', details: error.message });
    }
});

// API endpoint to fetch homework
app.get('/api/huiswerk', async (req, res) => {
    if (!currentUser) return res.status(401).json({ error: 'Niet ingelogd bij Somtoday.' });

    try {
        const today = new Date();
        const homeworkManager = currentUser.homeworkManager;

        // Fetch homework starting from today
        const homeworkCollection = await homeworkManager.fetchHomeworkAppointments(today);

        // Format the output
        const huiswerk = Array.from(homeworkCollection.values()).map(hw => ({
            id: hw.id,
            vak: hw.appointment ? hw.appointment.abbreviation : 'Onbekend vak',
            datum: hw.appointment ? hw.appointment.startValidity : hw.date,
            taak: hw.description,
            type: hw.homeworkType
        }));

        res.json({ huiswerk });
    } catch (error) {
        console.error('Fout bij ophalen huiswerk:', error);
        res.status(500).json({ error: 'Fout bij het ophalen van het huiswerk.', details: error.message });
    }
});

// Start the server
app.listen(port, () => {
    console.log(`
==================================================
🌟 Somtoday API Server gestart op poort ${port} 🌟
==================================================

Je kunt de UI bekijken op:
➡️  http://localhost:${port}

API Endpoints (handig voor AI):
- GET http://localhost:${port}/api/status
- GET http://localhost:${port}/api/rooster
- GET http://localhost:${port}/api/huiswerk
==================================================
`);
});
