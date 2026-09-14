"""
A short block of facts that must always be exact, regardless of how a
question is phrased or how retrieval scores that day: fee amounts, bank
details, the VC's name, etc.

This is intentionally small. It gets prepended to every prompt in rag.py
as "verified facts" that the model is told to trust over anything else in
the retrieved context if the two ever disagree.

IMPORTANT: these were carried over from the previous version of this
project's hardcoded responses, not freshly re-scraped — verify each line
against the current uetmardan.edu.pk before relying on this in production,
and update it whenever something changes (new VC, new fee amount, etc.).
Keeping this in one small file instead of scattered keyword-matching code
is the whole point: there's exactly one place to edit.
"""

VERIFIED_FACTS = """
Undergraduate application processing / prospectus fees: Rs. 2,000 for BS
Computer Science and other non-engineering programs. Rs. 1,500 for
engineering programs (BSc Electrical, Civil, Mechanical, Telecommunication,
and Computer Software Engineering). These are processing/prospectus fees
only, not the full tuition or semester fee. Payment goes to a Bank of Khyber
(BOK) account: PK55KHYB0179003004139436, branch code 0179, at any BOK branch
in Khyber Pakhtunkhwa.

Entrance test: engineering-program applicants must take the ETEA (Educational
Testing and Evaluation Agency) entrance test, administered by the Government
of Khyber Pakhtunkhwa.

Admission process: non-engineering applicants apply online through the
ugadmissions portal; engineering applicants apply through the engineering
admissions portal. Applicants upload scanned copies of required documents
and pay the processing fee at any BOK branch. Erstwhile FATA candidates may
also apply under the Open and Rationalized quota schemes; for FATA
reserved-quota seats, contact the Directorate of Admissions at UET Mardan or
UET Peshawar.

Vice Chancellor: Prof. Dr. Gul Muhammad Khan (verify this is still current
before relying on it — leadership changes over time).

Hostel accommodation: available for outstation students. Three hostels
currently (two for male students, one for female students), combined
capacity of roughly 380 students. Allocation is merit- and
availability-based, not guaranteed.

Governance: UET Mardan was established by the Government of Khyber
Pakhtunkhwa under the KP Universities Act, and its official public website
lists senior university officers such as the Vice Chancellor, Pro Vice
Chancellor, Registrar, Dean, Director Admissions, and Controller of
Examinations. The official site does not provide a public roster of a Board
of Governors in the pages checked here. For the exact composition of the
Board of Governors, contact the university directly through the Registrar or
University Secretariat; the official contact page lists Registrar at
Registrar@uetmardan.edu.pk and general email at info@uetmardan.edu.pk.

Departments: Electrical Engineering, Computer Software Engineering,
Telecommunication Engineering, Computer Science, Mechanical Engineering,
Civil Engineering, and Natural Sciences & Humanities. UET Mardan also has a
Center of Artificial Intelligence.

Undergraduate BS/BSc recurring fee range: the official 2024-25 undergraduate
prospectus shows fees varying by program and scheme; a rough recurring fee
range is roughly PKR 32,000 to 100,000 per semester. The lower end appears
in some open-merit / natural science pathways, while engineering and self-finance
tracks push higher, with recurring totals around PKR 51,000 for some open-merit
engineering programs and up to roughly PKR 98,000+ for some self-finance and
rationalized categories. Exact figures depend on the specific program and fee
scheme; the current BS fee page and admissions office should be checked for the
latest exact amounts.

BS Artificial Intelligence fee note: the local cached prospectus and admissions
materials do not list a separate, exact per-semester recurring fee for BS
Artificial Intelligence. The exact amount is scheme-dependent (for example,
open merit, rationalized, and self-finance categories) and the authoritative
current source is the official BS fee structure page: https://www.uetmardan.edu.pk/uetm/Admissions/bsfee.

Employment and HR details: the local cached data does not contain a verified,
current published age limit, salary range, or qualification comparison for
Lecturer, Junior Lecturer, or Assistant Professor posts at UET Mardan. For
these questions, the authoritative sources are the official UET Mardan
website, the Registrar/HR office, and the relevant department or vacancy
notice. The official contact page lists the Registrar at
Registrar@uetmardan.edu.pk and general university contact at
info@uetmardan.edu.pk. This applies especially to questions about lecturer,
assistant professor, or junior lecturer qualification standards, age limits,
advertised pay, or related HR requirements. Do not invent age limits, salary
figures, or qualification differences when the current notice is not available
in the scraped data.

Postgraduate programs offered at UET Mardan (based on the official
postgraduate prospectus and admissions criteria):
- M.Sc. Computer Software Engineering
- M.Sc. Electrical Engineering with specializations in Power Systems and
  Control Engineering and Communication and Electronics Engineering
- M.Sc. Renewable Energy Engineering
- M.Sc. Telecommunication Engineering
- MS Computer Science
- MS Mathematics
- Ph.D. Computer Software Engineering
- Ph.D. Electrical Engineering
- Ph.D. Telecommunication Engineering

IMPORTANT LINKS (verify these still work before relying on them; re-check
periodically since portals get restructured):
- Undergraduate admissions portal (non-engineering): https://uetmardan.edu.pk/ugadmissions
- Postgraduate (MS/PhD) admissions portal: https://uetmardan.edu.pk/pgadmissions
- Undergraduate prospectus: https://www.uetmardan.edu.pk/uetm/Prospectus/index
- Postgraduate prospectus: https://www.uetmardan.edu.pk/uetm/PGAdmissions/pgprospectus
- Admission schedule (undergraduate): https://www.uetmardan.edu.pk/uetm/Admissions/admissionschedule
- BS fee structure: https://www.uetmardan.edu.pk/uetm/Admissions/bsfee
- MS/PhD fee structure: https://www.uetmardan.edu.pk/uetm/PGAdmissions/msphdfee
- Scholarships: https://www.uetmardan.edu.pk/uetm/Scholarships/index
- Hostel information: https://www.uetmardan.edu.pk/uetm/Hostels
- Contact / official page: https://www.uetmardan.edu.pk/uetm/Contact

DOWNLOADABLE FORMS (PDF/Word — download, fill, and submit to the relevant
office; these are administrative/academic forms, NOT the admission
application itself, which is submitted online through the portals above):
- Application form for Transcript & Provisional Certificate (submit to
  Controller of Examinations): https://www.uetmardan.edu.pk/uetm/assets/files/downloads/Application_form_for_Transcript_v2.pdf
- Application form for Degree: https://www.uetmardan.edu.pk/uetm/assets/files/downloads/Application_form_for_Degree_v2.pdf
- Job Application Form (submit to Office of the Registrar): https://www.uetmardan.edu.pk/uetm/assets/files/downloads/21_Job-Application-Form.pdf
- Transportation Form: https://www.uetmardan.edu.pk/uetm/assets/files/downloads/11122020_UETM_Transportation_Form.pdf
- BSc Registration Form (Regular Courses): https://www.uetmardan.edu.pk/uetm/assets/files/downloads/260419-BSc-Registration-Form-Regular-courses.pdf
- Re-Registration Form: https://www.uetmardan.edu.pk/uetm/assets/files/downloads/260419-Re-registration-form.pdf
- PG Form-1, Student Registration Form (Word doc): https://www.uetmardan.edu.pk/uetm/assets/files/downloads/PG-Form-1%20_%20(Student%20Registration%20Form).docx
- Full downloads page (all other forms, policies, calendars): https://www.uetmardan.edu.pk/uetm/Download

The BS/MS/PhD admission APPLICATION ITSELF is not a downloadable form — it
is filled out online at the ugadmissions/engineering/pgadmissions portals
listed above. If a student asks about a form not in this list (e.g. course
withdrawal, semester freeze), do not guess a URL — point them to the full
downloads page above and suggest checking the relevant department or
examination office directly, since it may not have a standing form.
""".strip()