"""
Idempotent demo seed data: inserts sample documents into PostgreSQL, chunks text,
and upserts embeddings into ChromaDB (same path as API uploads).

Duplicate detection uses a stable `source` URI per document: `seed://demo/<slug>`.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document import Document
from app.models.user import User
from app.services.embeddings import replace_document_embedding
from app.services.ingestion import save_document_chunks, split_into_chunks

logger = logging.getLogger(__name__)

SEED_SOURCE_PREFIX = "seed://demo/"


@dataclass(frozen=True)
class SeedDocument:
    slug: str
    title: str
    category: str
    department: str
    owner: str
    body: str

    @property
    def source(self) -> str:
        return f"{SEED_SOURCE_PREFIX}{self.slug}"

    def full_content(self) -> str:
        header = (
            f"Document owner: {self.owner}\n"
            f"Owning department: {self.department}\n"
            f"Document category: {self.category}\n\n"
        )
        return (header + self.body.strip()).strip()


def _p(*parts: str) -> str:
    return "\n\n".join(s.strip() for s in parts if s and s.strip())


def _seed_definitions() -> list[SeedDocument]:
    """Twenty realistic internal policy documents (200+ words each)."""
    return [
        SeedDocument(
            slug="leave-policy",
            title="Annual Leave and Time-Off Policy",
            category="Policy",
            department="HR",
            owner="Maya Patel (Director of Human Resources)",
            body=_p(
                "This policy governs how employees request, schedule, and record paid and unpaid time away from work. "
                "It applies to regular full-time and part-time staff; contractors follow the terms of their agreements. "
                "Accruals begin after successful completion of probation unless local law or an offer letter specifies otherwise. "
                "Employees accrue annual leave monthly based on full-time equivalency; part-time schedules are pro-rated using standard hours.",
                "Requests must be submitted through the HR self-service portal. Planned vacation should be submitted at least ten business days in advance. "
                "Managers should approve or decline within two business days and may coordinate coverage to protect service levels. "
                "Emergency absences should be reported to the manager and HR as soon as practicable. "
                "Medical leave beyond five consecutive calendar days normally requires documentation from a licensed provider. "
                "Company holidays are published annually and do not reduce personal leave balances.",
                "Leave balances appear on pay advice and in the portal. A limited carry-forward may apply at year-end subject to caps. "
                "Patterns of unapproved absences, falsified requests, or abuse of sick leave may trigger review under the Employee Code of Conduct. "
                "HR maintains records for audits and statutory reporting. This policy is reviewed annually and may be revised to reflect regulatory updates.",
            ),
        ),
        SeedDocument(
            slug="employee-code-of-conduct",
            title="Employee Code of Conduct",
            category="Policy",
            department="HR",
            owner="James O'Neill (VP, People & Culture)",
            body=_p(
                "Every employee is expected to act with integrity, respect, and accountability. "
                "This code describes behaviors that protect customers, colleagues, and the company’s reputation. "
                "Harassment, discrimination, retaliation, and workplace violence are prohibited. "
                "Confidential information—including customer data, pricing, roadmaps, and personnel records—must be handled according to the Data Privacy Policy and need-to-know principles.",
                "Conflicts of interest must be disclosed promptly. Employees may not accept gifts or entertainment that could influence business decisions, except as permitted by the gifts and entertainment guideline. "
                "Use of company assets for unlawful activity, personal gain that harms the company, or unapproved side businesses that compete with the firm is not allowed. "
                "Accurate books and records are mandatory; falsification or coercion related to reporting is a serious violation.",
                "Reporting concerns through the ethics hotline or HR is encouraged and protected against retaliation when made in good faith. "
                "Violations may result in coaching, warnings, suspension, or termination depending on severity and repetition. "
                "Managers must escalate credible complaints quickly. The company may involve legal counsel and external investigators when appropriate. "
                "This code supplements local policies and employment contracts and is updated as laws and business risks evolve.",
            ),
        ),
        SeedDocument(
            slug="it-security-guidelines",
            title="IT Security Guidelines",
            category="IT",
            department="IT",
            owner="Priya Desai (Chief Information Security Officer)",
            body=_p(
                "These guidelines define minimum security practices for endpoints, networks, cloud services, and physical access to systems. "
                "All workforce members must use company-approved devices for work on company data unless an exception is formally granted. "
                "Full-disk encryption, automatic screen locks, and current antivirus or endpoint detection tooling are required where deployed. "
                "Administrative privileges are restricted and monitored; elevated access requires approval and periodic recertification.",
                "Remote access must use approved VPN or zero-trust clients. Split tunneling that exposes sensitive traffic is prohibited unless security approves a documented exception. "
                "Sensitive data must not be stored on personal devices or unapproved cloud drives. "
                "Security patches should be applied within published timelines. Vulnerability scanning and logging may be used to verify compliance.",
                "Incidents—including suspected malware, lost devices, or unauthorized access—must be reported immediately to the security operations channel. "
                "Phishing simulations and training are part of the control program; repeated failures may trigger additional coaching. "
                "Third-party integrations require review for data handling, availability, and contractual security clauses. "
                "Non-compliance can lead to access revocation and disciplinary action under company policy. "
                "Annual attestations capture acceptance of these controls, and managers review exceptions quarterly with remediation timelines. "
                "Metrics on failed logins and policy drift are monitored to prioritize improvements.",
            ),
        ),
        SeedDocument(
            slug="password-policy",
            title="Password and Authentication Policy",
            category="Policy",
            department="IT",
            owner="Carlos Mendez (IT Operations Manager)",
            body=_p(
                "Passwords and authentication factors protect accounts, email, source code, and customer information. "
                "Users must choose unique credentials for corporate systems and must not reuse personal passwords that appear in public breach lists. "
                "Minimum length, complexity, and rotation rules are enforced by the identity platform and may vary by system sensitivity. "
                "Multi-factor authentication is required for remote access, privileged roles, and high-risk applications.",
                "Passwords must not be shared, written on sticky notes in public areas, or embedded in code repositories. "
                "Service accounts and automation secrets must be stored in approved vaults with rotation schedules. "
                "If a password is suspected to be compromised, it must be changed immediately and the security team notified if indicators suggest active abuse.",
                "Administrators must use separate accounts for day-to-day work versus elevated tasks. "
                "Biometric and hardware tokens should be enrolled according to IT instructions. Lost tokens must be reported promptly. "
                "Periodic access reviews validate that accounts remain appropriate. Violations of authentication policy may result in account suspension and investigation. "
                "Emergency break-glass procedures exist for critical incidents and are tightly logged. "
                "Password managers approved by IT are encouraged to reduce reuse while maintaining complexity requirements.",
            ),
        ),
        SeedDocument(
            slug="remote-work-policy",
            title="Remote and Hybrid Work Policy",
            category="Policy",
            department="HR",
            owner="Amelia Grant (HR Business Partner)",
            body=_p(
                "This policy supports flexible remote and hybrid arrangements where role requirements and business needs allow. "
                "Eligibility depends on job duties, customer commitments, and security constraints documented with your manager. "
                "Approved remote workers must maintain a safe, ergonomically reasonable workspace and reliable connectivity for scheduled meetings. "
                "Core collaboration hours may be defined by the team to ensure overlap for planning and customer support.",
                "Employees working remotely remain subject to the Code of Conduct, confidentiality obligations, and time-tracking rules where applicable. "
                "Company equipment issued for home use must be used primarily for business purposes and protected against theft or unauthorized viewing. "
                "International work from unapproved locations is not permitted without HR and tax review due to regulatory and payroll complexity.",
                "Performance is evaluated on outcomes and responsibilities rather than physical presence alone. "
                "Managers should document expectations, check in regularly, and address performance issues promptly. "
                "The company may change hybrid schedules with reasonable notice when operational needs shift. "
                "Questions about accommodations or local law should be directed to HR. "
                "Temporary remote arrangements during office closures follow business continuity playbooks and may include alternate equipment shipping. "
                "Ergonomics stipends, where offered, must be used for approved items and documented per finance policy.",
            ),
        ),
        SeedDocument(
            slug="expense-reimbursement-policy",
            title="Expense Reimbursement Policy",
            category="Finance",
            department="Finance",
            owner="Elena Volkov (Corporate Controller)",
            body=_p(
                "Employees may be reimbursed for reasonable, necessary business expenses incurred while performing authorized duties. "
                "Eligible categories typically include travel, client hospitality within limits, training tuition when pre-approved, and small supplies when a corporate card is unavailable. "
                "Personal entertainment, non-business travel upgrades, and fines are generally not reimbursable. "
                "Receipts are required above the threshold stated in the finance portal; digital images are acceptable if legible.",
                "Claims must be submitted within forty-five days of incurring the expense and routed through the employee’s manager for approval. "
                "Allocations to cost centers and projects must be accurate to support budgeting and client billing where applicable. "
                "Advances, if offered, must be reconciled on time; repeated delays may affect future advance eligibility.",
                "Tax treatment of reimbursements follows local regulations; some items may be treated as taxable benefits. "
                "Finance may audit samples of claims and request additional documentation. "
                "Fraudulent or duplicate submissions may lead to repayment, discipline, and referral to legal authorities. "
                "Procurement policies govern preferred vendors and corporate card usage; employees should consult finance before large commitments. "
                "Corporate cardholders must reconcile statements within the published cycle and attach itemized receipts for any flagged transactions. "
                "Mileage and per diem rates are updated annually and communicated through the finance portal.",
            ),
        ),
        SeedDocument(
            slug="data-privacy-policy",
            title="Data Privacy and Protection Policy",
            category="Policy",
            department="IT",
            owner="Priya Desai (Chief Information Security Officer)",
            body=_p(
                "This policy describes how the organization collects, uses, stores, and deletes personal data in line with applicable privacy laws and contractual commitments. "
                "Data must be collected for specified, legitimate purposes and retained only as long as necessary for those purposes or legal obligations. "
                "Individuals may have rights to access, correction, deletion, or restriction depending on jurisdiction; requests must be routed through the privacy office for consistent handling.",
                "Technical controls include role-based access, encryption for sensitive data at rest and in transit where appropriate, and logging of administrative actions. "
                "Data transfers across borders require approved mechanisms such as standard contractual clauses or adequacy decisions. "
                "Vendors that process personal data must sign data protection agreements and demonstrate security practices.",
                "Employees must classify information correctly, avoid oversharing in tickets or chat, and verify recipient identities before disclosing sensitive details. "
                "Breaches or suspected breaches must be escalated immediately to allow assessment and notification timelines. "
                "Training reinforces phishing awareness and secure handling of customer records. "
                "Privacy impact assessments may be required for new products. Non-compliance can harm customers and expose the company to regulatory penalties. "
                "Data minimization exercises periodically review fields collected in forms and integrations to remove unnecessary attributes. "
                "Retention schedules are published by data category and must be followed when decommissioning systems or backups.",
            ),
        ),
        SeedDocument(
            slug="onboarding-process",
            title="Employee Onboarding Process",
            category="HR",
            department="HR",
            owner="Sofia Nguyen (Talent Operations Lead)",
            body=_p(
                "Onboarding integrates new hires into teams, systems, and culture during their first weeks. "
                "Before day one, IT provisions accounts, facilities prepares access badges where applicable, and HR confirms eligibility and payroll setup. "
                "Managers prepare a thirty-sixty-ninety day plan with clear outcomes, introductions, and training milestones. "
                "New employees complete required compliance training—including security, harassment prevention, and data handling—within published deadlines.",
                "Orientation sessions explain benefits, time reporting, expense tools, and internal communication norms. "
                "Buddy programs pair newcomers with experienced colleagues for informal questions. "
                "Checkpoints at two weeks and thirty days review progress, tooling gaps, and engagement. Feedback is used to improve the program.",
                "International hires may have additional steps for visas, equipment shipping, and local statutory enrollments coordinated with mobility specialists. "
                "Contractors follow a streamlined track aligned to their statements of work. "
                "HR tracks completion metrics and audits training records for audits. "
                "Successful onboarding reduces time-to-productivity and supports retention; managers are accountable for timely task completion. "
                "Role-specific technical ramp plans may include shadowing, sandbox environments, and certification targets within the first ninety days. "
                "Feedback from new hires is collected anonymously to refine orientation content and scheduling. "
                "Equipment return logistics for remote hires include prepaid shipping labels and secure wipe attestations where required.",
            ),
        ),
        SeedDocument(
            slug="performance-review-guidelines",
            title="Performance Review Guidelines",
            category="HR",
            department="HR",
            owner="Daniel Brooks (Head of Performance & Rewards)",
            body=_p(
                "Performance reviews document achievements, growth areas, and goals in a fair, evidence-based manner. "
                "Managers should maintain ongoing feedback throughout the year rather than relying solely on an annual conversation. "
                "Ratings, where used, must be supported by examples tied to role expectations and company values. "
                "Bias awareness is critical: calibrate across teams to ensure consistent standards for similar roles.",
                "Employees are encouraged to self-reflect, gather peer input where appropriate, and propose development plans including training, stretch assignments, or mentorship. "
                "Documentation should be factual and respectful; subjective labels without examples are discouraged. "
                "Performance improvement plans may be used when gaps are significant, with clear metrics and check-in dates.",
                "Compensation discussions may be separated from review conversations depending on regional practice. "
                "Disagreements can be escalated to HR for facilitation. Records are retained according to policy and may be referenced for promotions or restructuring. "
                "Remote employees receive the same review cadence and support. "
                "HR offers templates, training for new managers, and analytics to leadership on completion rates and calibration health. "
                "Underperformers receive documented expectations, support resources, and timelines before any adverse outcomes where policy requires. "
                "Calibration sessions compare ratings across org units to surface outliers and document rationale for leadership review.",
            ),
        ),
        SeedDocument(
            slug="salary-structure",
            title="Salary Bands and Compensation Structure",
            category="Finance",
            department="Finance",
            owner="Marcus Li (Director, Total Rewards)",
            body=_p(
                "The compensation structure defines job families, levels, and salary ranges designed to attract and retain talent while maintaining internal equity and fiscal discipline. "
                "Ranges are benchmarked against market surveys and reviewed periodically; geographic differentials may apply where the company operates multiple locations. "
                "Offers must align to approved bands unless an exception is documented with HR and finance leadership. "
                "Equity grants, where available, follow separate guidelines tied to level, performance, and retention goals.",
                "Promotion or lateral moves may trigger range changes after calibration. "
                "Employees receive communication about how ranges relate to their role and how variable pay components work. "
                "Pay transparency obligations in certain jurisdictions are honored through postings or individualized disclosures as required by law.",
                "Managers do not determine ranges unilaterally; partnership with HR ensures consistency and compliance. "
                "Pay equity analyses help identify unintended gaps; remediation plans may be implemented confidentially. "
                "Questions about total rewards should go to HR; speculation or peer comparisons in public channels should be avoided to reduce misunderstanding. "
                "This overview does not constitute a contract; detailed plans are maintained in the rewards handbook. "
                "Spot bonuses and retention awards follow separate approval matrices and may not be combined arbitrarily with base salary changes. "
                "Employees should direct detailed questions to their manager or HR partner rather than informal peer comparisons.",
            ),
        ),
        SeedDocument(
            slug="cybersecurity-awareness",
            title="Cybersecurity Awareness Program",
            category="IT",
            department="IT",
            owner="Hannah Frost (Security Awareness Lead)",
            body=_p(
                "Cybersecurity is a shared responsibility. This program educates employees on threats such as phishing, business email compromise, ransomware, and unsafe browser extensions. "
                "Participants learn to verify sender domains, avoid clicking suspicious links, and report messages using the phishing button. "
                "Simulated campaigns measure resilience; individuals who repeatedly fall for simulations receive targeted coaching rather than public shaming.",
                "Safe handling of removable media, clean desk practices, and traveler precautions for conferences are included. "
                "Developers receive supplemental training on secure coding basics and secrets management. "
                "Contractors with system access complete the same baseline modules annually.",
                "Metrics on completion rates and simulation outcomes are reported to leadership; teams below target may schedule live workshops. "
                "Resources include quick-reference guides, office hours with security champions, and recorded sessions for asynchronous learning. "
                "Reporting suspected incidents early limits damage and may be required by policy or regulation. "
                "The curriculum updates as attackers evolve; employees should expect periodic refreshers. "
                "Strong awareness reduces breach likelihood and supports customer trust in our services. "
                "Role-based learning paths add modules for finance, HR, and executives handling sensitive workflows. "
                "Completion certificates are stored for audit evidence and must be renewed before access renewals where required.",
            ),
        ),
        SeedDocument(
            slug="travel-policy",
            title="Business Travel Policy",
            category="Finance",
            department="Finance",
            owner="Oliver Stone (Travel & Expense Manager)",
            body=_p(
                "Business travel should be booked through approved channels to leverage corporate rates, duty-of-care tracking, and consolidated invoicing. "
                "Travelers must obtain manager approval before incurring non-refundable costs. "
                "Economy class is standard for domestic flights unless medical needs or long-haul policies specify otherwise. "
                "Accommodation should meet reasonable safety and comfort standards without luxury upgrades unless client obligations require them and are pre-approved.",
                "Per diems or meal caps may apply by region; alcohol is reimbursable only when directly tied to client entertainment within limits. "
                "Ground transportation favors ride-hail programs or rental cars sized to need; personal vehicle mileage follows the published rate when authorized. "
                "International travel may require security briefings, vaccinations, and registration with the travel risk provider.",
                "Travelers must follow export control and device security rules, especially when crossing borders with laptops containing source code or customer data. "
                "Unused tickets and credits should be tracked to avoid waste. "
                "During emergencies, employees should follow guidance from the crisis communications team. "
                "Violations—such as personal trips billed to the company—may trigger repayment and discipline. "
                "Finance periodically updates this policy to reflect vendor contracts and regulatory requirements. "
                "Travelers should keep itineraries updated in the travel tool so duty-of-care alerts reach them during disruptions. "
                "Personal travel extensions may be permitted when employees pay incremental costs directly and obtain written approval.",
            ),
        ),
        SeedDocument(
            slug="work-from-home-rules",
            title="Work From Home Rules (Sales)",
            category="Policy",
            department="Sales",
            owner="Rachel Kim (Regional Sales Director)",
            body=_p(
                "Sales professionals working from home must maintain professional availability during agreed customer-facing windows and update CRM records in a timely manner. "
                "Home offices should present a neutral background on video calls and minimize background noise during client conversations. "
                "Demo equipment, samples, and promotional materials must be stored securely to protect pricing and partner information.",
                "Travel for customer visits should follow the Business Travel Policy; hybrid sellers balance remote work with in-person engagement as territory plans require. "
                "Commission plans and quotas remain in effect regardless of location; disputes follow the sales operations escalation path. "
                "Collaboration with solutions engineers and legal on proposals protects margin and contractual risk.",
                "IT-approved headsets and connectivity tools are recommended to ensure call quality. "
                "Personal use of company laptops for high-risk downloads is prohibited. "
                "Local labor posters and break rules still apply based on the employee’s jurisdiction. "
                "Managers conduct pipeline reviews and forecast hygiene checks to keep remote teams aligned. "
                "This guidance complements the broader Remote and Hybrid Work Policy and may be updated with sales leadership input. "
                "Regional holidays and customer blackout periods should be reflected in calendars to avoid missed commitments. "
                "Sales contests and SPIFF communications must be vetted by legal and finance before broadcast to the field.",
            ),
        ),
        SeedDocument(
            slug="internal-communication-guidelines",
            title="Internal Communication Guidelines",
            category="Admin",
            department="Sales",
            owner="Victor Alam (Internal Communications Manager)",
            body=_p(
                "Clear internal communication reduces duplicated work and keeps teams aligned on priorities. "
                "Use the right channel: urgent operational issues belong in designated chat spaces with on-call tags; long-form decisions belong in documentation or email with clear owners. "
                "Subject lines and thread titles should be specific enough to retrieve later. "
                "All-staff announcements go through comms or executive approval to avoid conflicting messages.",
                "Respect working hours across time zones; schedule messages when possible and mark after-hours messages as non-urgent unless truly critical. "
                "Inclusive language and accessible formatting—headings, alt text for important images—help everyone participate. "
                "Do not share material non-public financial data or customer names in open channels without need and approval.",
                "Feedback should be constructive and directed to individuals privately when sensitive. "
                "Leaders should model concise updates and acknowledge receipt to close loops. "
                "Town halls and Q&A forums should surface themes to leadership without exposing confidential details. "
                "Metrics on channel noise may trigger guidelines refresher sessions. "
                "These norms support psychological safety and operational clarity across sales and corporate functions. "
                "Crisis communications playbooks define approval chains for customer-impacting incidents and should be referenced before ad hoc posts. "
                "Internal blogs and newsletters follow editorial calendars coordinated with product and marketing leadership.",
            ),
        ),
        SeedDocument(
            slug="project-management-sop",
            title="Project Management Standard Operating Procedure",
            category="Admin",
            department="IT",
            owner="Nina Okonkwo (Program Management Office Lead)",
            body=_p(
                "Projects delivering technology change follow this SOP from intake through closure. "
                "Requests are triaged for strategic alignment, risk, and capacity; a charter summarizes scope, success metrics, stakeholders, and dependencies. "
                "Work is planned in phases with milestones; agile teams maintain backlogs with definition of ready and definition of done. "
                "Risks and issues are logged with owners and due dates; escalations follow the governance map.",
                "Testing includes functional, regression, and security checks appropriate to the change class. "
                "Release management uses approved windows, rollback plans, and communication templates for internal and external audiences when customer impact exists. "
                "Documentation is stored in the knowledge base with version history.",
                "Post-implementation reviews capture lessons learned and actual benefits versus forecast. "
                "Project artifacts may be audited for compliance with SDLC policy. "
                "PMO provides templates, training, and portfolio reporting; teams may adapt ceremonies but must retain traceability. "
                "Vendor-led projects require joint steering and exit criteria. "
                "Skipping mandatory controls requires documented risk acceptance from accountable executives. "
                "Dependency mapping across teams is maintained to avoid surprise blockers during integration milestones. "
                "Benefits realization tracking compares forecasted ROI to actual outcomes for major initiatives. "
                "Steering committees review scope changes against original business cases before approving funding shifts.",
            ),
        ),
        SeedDocument(
            slug="meeting-guidelines",
            title="Meeting Guidelines and Etiquette",
            category="Admin",
            department="Sales",
            owner="Laura Schmidt (Sales Operations)",
            body=_p(
                "Meetings should have a purpose, an agenda distributed in advance, and a designated facilitator who keeps time. "
                "Default lengths can often be shortened; consider async updates before scheduling. "
                "Required attendees should be limited to decision makers and contributors; others receive notes. "
                "Recordings and notes respect confidentiality and data minimization; do not record unless all participants consent where required.",
                "Start and end on time to respect colleagues’ calendars. "
                "Action items need owners and deadlines captured in the task system, not only in chat. "
                "One-on-ones remain private; skip-level meetings should have transparent goals.",
                "Large forums use structured Q&A and moderation to ensure diverse voices are heard. "
                "Sales review meetings focus on pipeline health, risks to forecast, and customer outcomes rather than activity volume alone. "
                "Follow-up communications summarize decisions to reduce ambiguity. "
                "Repeated ineffective meetings should be redesigned with facilitation support. "
                "These guidelines apply across functions and complement tooling-specific training for video platforms. "
                "Calendar hygiene—including declining meetings when optional—helps colleagues plan realistically. "
                "Read-ahead materials should be linked in invites so decisions are informed without repeating lengthy status reads aloud. "
                "Recurring meetings should be revalidated quarterly to confirm they still serve a purpose.",
            ),
        ),
        SeedDocument(
            slug="software-usage-policy",
            title="Software Usage and Licensing Policy",
            category="Policy",
            department="IT",
            owner="Carlos Mendez (IT Operations Manager)",
            body=_p(
                "Software installed on company devices or used to process company data must be properly licensed and approved. "
                "Employees must not install unvetted applications that introduce malware risk or violate vendor agreements. "
                "Open-source components in products must comply with license obligations tracked by engineering governance.",
                "IT maintains a catalog of standard tools for productivity, collaboration, and security. "
                "Requests for new tools go through procurement and security review for data residency, SSO support, and integration costs. "
                "Shadow IT—using personal SaaS accounts for company data—is prohibited without exception processes.",
                "License true-ups are forecasted during budgeting; over-deployment may incur true-up fees or compliance exposure. "
                "Software access is removed promptly when roles change or employment ends. "
                "Developers must not embed API keys in repositories; secret scanning hooks help enforce this. "
                "Violations may lead to license remediation costs and disciplinary steps. "
                "Questions about acceptable alternatives should be raised early to avoid rework. "
                "Software evaluations include trial periods with security review before production data is loaded. "
                "End-of-life tools are sunset with migration plans communicated to affected teams. "
                "Trial licenses must not exceed vendor terms, and usage data may be reviewed to validate adoption before renewal.",
            ),
        ),
        SeedDocument(
            slug="company-vision-mission",
            title="Company Vision, Mission, and Values",
            category="Policy",
            department="Sales",
            owner="Alex Rivera (Chief Revenue Officer)",
            body=_p(
                "Our mission is to deliver reliable solutions that help customers achieve measurable outcomes while building durable partnerships. "
                "The vision is to be the most trusted partner in our markets through innovation, execution excellence, and ethical conduct. "
                "Values include customer obsession, accountability, inclusion, and continuous learning. "
                "Sales teams translate this mission into discovery conversations that uncover real problems rather than pushing unnecessary products.",
                "We compete fairly and respect confidentiality of prospect information obtained during evaluations. "
                "Partnerships with resellers and integrators follow clear rules of engagement to avoid channel conflict. "
                "Pricing integrity matters: discounts require documented approvals aligned to deal strategy.",
                "Community involvement and sustainability commitments are part of how we show responsibility beyond revenue targets. "
                "Leaders reinforce values through recognition programs and by addressing behavior inconsistent with our standards. "
                "This statement is shared with new hires and updated periodically with board input. "
                "It guides strategic planning and helps prioritize investments that reinforce long-term trust over short-term wins. "
                "Customer references and case studies follow brand review to ensure accuracy and consent. "
                "Ethical selling training reinforces anti-bribery expectations and third-party due diligence for partners. "
                "Win-loss reviews are conducted with product and marketing to sharpen positioning without disparaging competitors.",
            ),
        ),
        SeedDocument(
            slug="attendance-policy",
            title="Attendance and Punctuality Policy",
            category="Policy",
            department="HR",
            owner="Maya Patel (Director of Human Resources)",
            body=_p(
                "Regular attendance and punctuality support teamwork, customer commitments, and fair workload distribution. "
                "Employees are expected to work scheduled hours and notify their manager when they will be late or absent except in emergencies. "
                "Hourly employees must record time accurately; salaried employees should coordinate flexibility within team norms. "
                "Excessive tardiness or unexplained absences may trigger coaching and, if unresolved, corrective action.",
                "Medical or disability-related attendance issues may require an interactive process to identify reasonable accommodations consistent with law. "
                "Weather or transit disruptions should be communicated as early as possible; safety takes priority over rigid clock times when authorized by policy.",
                "On-site roles may have different punctuality expectations than fully remote roles; job descriptions and team agreements clarify this. "
                "Overtime for non-exempt roles must be pre-approved where required. "
                "Attendance records are maintained for payroll and compliance; falsification is a serious offense. "
                "Managers should apply standards consistently and document patterns. "
                "HR provides guidance on local rules and union agreements where applicable. "
                "This policy works alongside leave policies and does not replace statutory entitlements. "
                "Flexible schedules still require core availability windows unless an individual accommodation specifies otherwise. "
                "Time fraud—including buddy punching or altering records—may result in immediate termination and legal referral.",
            ),
        ),
        SeedDocument(
            slug="exit-policy",
            title="Voluntary and Involuntary Exit Policy",
            category="Policy",
            department="HR",
            owner="James O'Neill (VP, People & Culture)",
            body=_p(
                "This policy outlines steps when an employee leaves the organization voluntarily or when employment ends for other reasons. "
                "Voluntary resignations should be submitted in writing with notice periods per contract or local law. "
                "Managers conduct knowledge transfer planning, return of assets, and access revocation coordination with IT. "
                "Exit interviews offer confidential feedback to improve the workplace; participation is encouraged but voluntary where permitted.",
                "Final pay, unused leave payouts, and benefits continuation options are explained according to jurisdiction. "
                "Company property—including laptops, badges, cards, and documents—must be returned promptly. "
                "Post-employment restrictions on solicitation or confidential information remain in effect as per signed agreements.",
                "Involuntary separations follow a review process with HR and legal to reduce bias and ensure documentation. "
                "Workforce reductions may include selection criteria, severance frameworks, and notification timelines aligned to regulation. "
                "Security escorts on site may be used when policy requires; communications are crafted to protect dignity and reduce business disruption. "
                "Alumni networks and references are handled consistently with reference policy. "
                "Managers must not make promises outside approved frameworks. "
                "COBRA or local continuation coverage notices are distributed within statutory deadlines, and equity vesting follows plan documents. "
                "Rehire eligibility may be noted in HR systems for future applications, subject to business needs and prior conduct.",
            ),
        ),
    ]


def seed_demo_documents(db: Session) -> dict[str, int]:
    """
    Insert demo documents if missing (matched by stable `source`), chunk text, and upsert embeddings.

    Returns counts: inserted, skipped, failed (failed should stay 0 in normal runs).
    """
    admin = db.query(User).filter(User.email == settings.seed_admin_email).first()
    if not admin:
        logger.error("Seed admin user not found (%s); run seed_default_admin first.", settings.seed_admin_email)
        raise RuntimeError("Seed admin user is required before seeding documents.")

    inserted = 0
    skipped = 0
    failed = 0

    for definition in _seed_definitions():
        try:
            existing = db.query(Document).filter(Document.source == definition.source).first()
            if existing:
                skipped += 1
                logger.info("Skipping existing seed document: %s", definition.source)
                continue

            document = Document(
                title=definition.title,
                category=definition.category,
                source=definition.source,
                file_name=None,
                content=definition.full_content(),
                department=definition.department,
                owner_id=admin.id,
            )
            db.add(document)
            db.commit()
            db.refresh(document)

            chunks = split_into_chunks(document.content)
            save_document_chunks(db, document.id, chunks)

            replace_document_embedding(
                document.id,
                document.content,
                document.department,
                document.title,
                document.category,
                document.source,
            )
            inserted += 1
            logger.info("Seeded document id=%s title=%r", document.id, document.title)
        except Exception:
            failed += 1
            logger.exception("Failed to seed document %s", definition.source)
            db.rollback()

    return {"inserted": inserted, "skipped": skipped, "failed": failed}
