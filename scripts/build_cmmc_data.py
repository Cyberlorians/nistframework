#!/usr/bin/env python3
"""
Generate the authoritative cmmc_data.json for CMMC 2.0 Levels 1-3.

Sources:
  - Level 1 (15 practices): FAR 52.204-21(b)(1)(i)-(xv)
  - Level 2 (110 practices, includes L1 as subset): NIST SP 800-171 R2
  - Level 3 (24 practices): NIST SP 800-172, selected per 32 CFR 170.14(c)(4) Table 1

Total unique: 15 L1 + 95 L2-only + 24 L3 = 134 entries
"""
import json
import os

# ---------------------------------------------------------------------------
# Family mapping: NIST section -> (family_code, family_name)
# ---------------------------------------------------------------------------
FAMILIES = {
    "3.1":  ("AC", "Access Control"),
    "3.2":  ("AT", "Awareness and Training"),
    "3.3":  ("AU", "Audit and Accountability"),
    "3.4":  ("CM", "Configuration Management"),
    "3.5":  ("IA", "Identification and Authentication"),
    "3.6":  ("IR", "Incident Response"),
    "3.7":  ("MA", "Maintenance"),
    "3.8":  ("MP", "Media Protection"),
    "3.9":  ("PS", "Personnel Security"),
    "3.10": ("PE", "Physical Protection"),
    "3.11": ("RA", "Risk Assessment"),
    "3.12": ("CA", "Security Assessment"),
    "3.13": ("SC", "System and Communications Protection"),
    "3.14": ("SI", "System and Information Integrity"),
}

# ---------------------------------------------------------------------------
# The 17 NIST 800-171 R2 controls mapped from FAR 52.204-21(b)(1)(i)-(xv)
# 15 FAR paragraphs -> 17 controls (FAR b.1.ix splits into 3.10.3/3.10.4/3.10.5)
# ---------------------------------------------------------------------------
L1_CONTROLS = {
    "3.1.1", "3.1.2", "3.1.20", "3.1.22",
    "3.5.1", "3.5.2",
    "3.8.3",
    "3.10.1", "3.10.3", "3.10.4", "3.10.5",
    "3.13.1", "3.13.5",
    "3.14.1", "3.14.2", "3.14.4", "3.14.5",
}

# ---------------------------------------------------------------------------
# Complete NIST SP 800-171 R2 control catalog (110 controls, 14 families)
# These form Level 1 (15 subset) + Level 2 (all 110)
# ---------------------------------------------------------------------------
NIST_800_171 = {
    # 3.1 Access Control (22)
    "3.1.1":  "Limit system access to authorized users, processes acting on behalf of authorized users, and devices (including other systems)",
    "3.1.2":  "Limit system access to the types of transactions and functions that authorized users are permitted to execute",
    "3.1.3":  "Control the flow of CUI in accordance with approved authorizations",
    "3.1.4":  "Separate the duties of individuals to reduce the risk of malevolent activity without collusion",
    "3.1.5":  "Employ the principle of least privilege, including for specific security functions and privileged accounts",
    "3.1.6":  "Use non-privileged accounts or roles when accessing nonsecurity functions",
    "3.1.7":  "Prevent non-privileged users from executing privileged functions and capture the execution of such functions in audit logs",
    "3.1.8":  "Limit unsuccessful logon attempts",
    "3.1.9":  "Provide privacy and security notices consistent with applicable CUI rules",
    "3.1.10": "Use session lock with pattern-hiding displays to prevent access and viewing of data after a period of inactivity",
    "3.1.11": "Terminate (automatically) a user session after a defined condition",
    "3.1.12": "Monitor and control remote access sessions",
    "3.1.13": "Employ cryptographic mechanisms to protect the confidentiality of remote access sessions",
    "3.1.14": "Route remote access via managed access control points",
    "3.1.15": "Authorize remote execution of privileged commands and remote access to security-relevant information",
    "3.1.16": "Authorize wireless access prior to allowing such connections",
    "3.1.17": "Protect wireless access using authentication and encryption",
    "3.1.18": "Control connection of mobile devices",
    "3.1.19": "Encrypt CUI on mobile devices and mobile computing platforms",
    "3.1.20": "Verify and control/limit connections to and use of external systems",
    "3.1.21": "Limit use of portable storage devices on external systems",
    "3.1.22": "Control CUI posted or processed on publicly accessible systems",

    # 3.2 Awareness and Training (3)
    "3.2.1":  "Ensure that managers, systems administrators, and users of organizational systems are made aware of the security risks associated with their activities and of the applicable policies, standards, and procedures related to the security of those systems",
    "3.2.2":  "Ensure that organizational personnel are adequately trained to carry out their assigned information security-related duties and responsibilities",
    "3.2.3":  "Provide security awareness training on recognizing and reporting potential indicators of insider threat",

    # 3.3 Audit and Accountability (9)
    "3.3.1":  "Create and retain system audit logs and records to the extent needed to enable the monitoring, analysis, investigation, and reporting of unlawful or unauthorized system activity",
    "3.3.2":  "Ensure that the actions of individual system users can be uniquely traced to those users so they can be held accountable for their actions",
    "3.3.3":  "Review and update logged events",
    "3.3.4":  "Alert in the event of an audit logging process failure",
    "3.3.5":  "Correlate audit record review, analysis, and reporting processes for investigation and response to indications of unlawful, unauthorized, suspicious, or unusual activity",
    "3.3.6":  "Provide audit record reduction and report generation to support on-demand analysis and reporting",
    "3.3.7":  "Provide a system capability that compares and synchronizes internal system clocks with an authoritative source to generate time stamps for audit records",
    "3.3.8":  "Protect audit information and audit logging tools from unauthorized access, modification, and deletion",
    "3.3.9":  "Limit management of audit logging functionality to a subset of privileged users",

    # 3.4 Configuration Management (9)
    "3.4.1":  "Establish and maintain baseline configurations and inventories of organizational systems (including hardware, software, firmware, and documentation) throughout the respective system development life cycles",
    "3.4.2":  "Establish and enforce security configuration settings for information technology products employed in organizational systems",
    "3.4.3":  "Track, review, approve or disapprove, and log changes to organizational systems",
    "3.4.4":  "Analyze the security impact of changes prior to implementation",
    "3.4.5":  "Define, document, approve, and enforce physical and logical access restrictions associated with changes to organizational systems",
    "3.4.6":  "Employ the principle of least functionality by configuring organizational systems to provide only essential capabilities",
    "3.4.7":  "Restrict, disable, or prevent the use of nonessential programs, functions, ports, protocols, and services",
    "3.4.8":  "Apply deny-by-exception (blacklisting) policy to prevent the use of unauthorized software or deny-all, permit-by-exception (whitelisting) policy to allow the execution of authorized software",
    "3.4.9":  "Control and monitor user-installed software",

    # 3.5 Identification and Authentication (11)
    "3.5.1":  "Identify system users, processes acting on behalf of users, and devices",
    "3.5.2":  "Authenticate (or verify) the identities of users, processes, or devices, as a prerequisite to allowing access to organizational systems",
    "3.5.3":  "Use multifactor authentication for local and network access to privileged accounts and for network access to non-privileged accounts",
    "3.5.4":  "Employ replay-resistant authentication mechanisms for network access to privileged and non-privileged accounts",
    "3.5.5":  "Prevent reuse of identifiers for a defined period",
    "3.5.6":  "Disable identifiers after a defined period of inactivity",
    "3.5.7":  "Enforce a minimum password complexity and change of characters when new passwords are created",
    "3.5.8":  "Prohibit password reuse for a specified number of generations",
    "3.5.9":  "Allow temporary password use for system logons with an immediate change to a permanent password",
    "3.5.10": "Store and transmit only cryptographically-protected passwords",
    "3.5.11": "Obscure feedback of authentication information",

    # 3.6 Incident Response (3)
    "3.6.1":  "Establish an operational incident-handling capability for organizational systems that includes preparation, detection, analysis, containment, recovery, and user response activities",
    "3.6.2":  "Track, document, and report incidents to designated officials and/or authorities both internal and external to the organization",
    "3.6.3":  "Test the organizational incident response capability",

    # 3.7 Maintenance (6)
    "3.7.1":  "Perform maintenance on organizational systems",
    "3.7.2":  "Provide controls on the tools, techniques, mechanisms, and personnel used to conduct system maintenance",
    "3.7.3":  "Ensure equipment removed for off-site maintenance is sanitized of any CUI",
    "3.7.4":  "Check media containing diagnostic and test programs for malicious code before the media are used in organizational systems",
    "3.7.5":  "Require multifactor authentication to establish nonlocal maintenance sessions via external network connections and terminate such connections when nonlocal maintenance is complete",
    "3.7.6":  "Supervise the maintenance activities of maintenance personnel without required access authorization",

    # 3.8 Media Protection (9)
    "3.8.1":  "Protect (i.e., physically control and securely store) system media containing CUI, both paper and digital",
    "3.8.2":  "Limit access to CUI on system media to authorized users",
    "3.8.3":  "Sanitize or destroy system media containing CUI before disposal or release for reuse",
    "3.8.4":  "Mark media with necessary CUI markings and distribution limitations",
    "3.8.5":  "Control access to media containing CUI and maintain accountability for media during transport outside of controlled areas",
    "3.8.6":  "Implement cryptographic mechanisms to protect the confidentiality of CUI stored on digital media during transport unless otherwise protected by alternative physical safeguards",
    "3.8.7":  "Control the use of removable media on system components",
    "3.8.8":  "Prohibit the use of portable storage devices when such devices have no identifiable owner",
    "3.8.9":  "Protect the confidentiality of backup CUI at storage locations",

    # 3.9 Personnel Security (2)
    "3.9.1":  "Screen individuals prior to authorizing access to organizational systems containing CUI",
    "3.9.2":  "Ensure that organizational systems containing CUI are protected during and after personnel actions such as terminations and transfers",

    # 3.10 Physical Protection (6)
    "3.10.1": "Limit physical access to organizational systems, equipment, and the respective operating environments to authorized individuals",
    "3.10.2": "Protect and monitor the physical facility and support infrastructure for organizational systems",
    "3.10.3": "Escort visitors and monitor visitor activity",
    "3.10.4": "Maintain audit logs of physical access",
    "3.10.5": "Control and manage physical access devices",
    "3.10.6": "Enforce safeguarding measures for CUI at alternate work sites",

    # 3.11 Risk Assessment (3)
    "3.11.1": "Periodically assess the risk to organizational operations, organizational assets, and individuals, resulting from the operation of organizational systems and the associated processing, storage, or transmission of CUI",
    "3.11.2": "Scan for vulnerabilities in organizational systems and applications periodically and when new vulnerabilities affecting those systems and applications are identified",
    "3.11.3": "Remediate vulnerabilities in accordance with risk assessments",

    # 3.12 Security Assessment (4)
    "3.12.1": "Periodically assess the security controls in organizational systems to determine if the controls are effective in their application",
    "3.12.2": "Develop and implement plans of action designed to correct deficiencies and reduce or eliminate vulnerabilities in organizational systems",
    "3.12.3": "Monitor security controls on an ongoing basis to ensure the continued effectiveness of the controls",
    "3.12.4": "Develop, document, and periodically update system security plans that describe system boundaries, system environments of operation, how security requirements are implemented, and the relationships with or connections to other systems",

    # 3.13 System and Communications Protection (16)
    "3.13.1":  "Monitor, control, and protect communications at the external boundaries and key internal boundaries of organizational systems",
    "3.13.2":  "Employ architectural designs, software development techniques, and systems engineering principles that promote effective information security within organizational systems",
    "3.13.3":  "Separate user functionality from system management functionality",
    "3.13.4":  "Prevent unauthorized and unintended information transfer via shared system resources",
    "3.13.5":  "Implement subnetworks for publicly accessible system components that are physically or logically separated from internal networks",
    "3.13.6":  "Deny network communications traffic by default and allow network communications traffic by exception (i.e., deny all, permit by exception)",
    "3.13.7":  "Prevent remote devices from simultaneously establishing non-remote connections with organizational systems and communicating via some other connection to resources in external networks (i.e., split tunneling)",
    "3.13.8":  "Implement cryptographic mechanisms to prevent unauthorized disclosure of CUI during transmission unless otherwise protected by alternative physical safeguards",
    "3.13.9":  "Terminate network connections associated with communications sessions at the end of the sessions or after a defined period of inactivity",
    "3.13.10": "Establish and manage cryptographic keys for cryptography employed in organizational systems",
    "3.13.11": "Employ FIPS-validated cryptography when used to protect the confidentiality of CUI",
    "3.13.12": "Prohibit remote activation of collaborative computing devices and provide indication of devices in use to users present at the device",
    "3.13.13": "Control and monitor the use of mobile code",
    "3.13.14": "Control and monitor the use of Voice over Internet Protocol (VoIP) technologies",
    "3.13.15": "Protect the authenticity of communications sessions",
    "3.13.16": "Protect the confidentiality of CUI at rest",

    # 3.14 System and Information Integrity (7)
    "3.14.1": "Identify, report, and correct system flaws in a timely manner",
    "3.14.2": "Provide protection from malicious code at designated locations within organizational systems",
    "3.14.3": "Monitor system security alerts and advisories and take action in response",
    "3.14.4": "Update malicious code protection mechanisms when new releases are available",
    "3.14.5": "Perform periodic scans of organizational systems and real-time scans of files from external sources as files are downloaded, opened, or executed",
    "3.14.6": "Monitor organizational systems, including inbound and outbound communications traffic, to detect attacks and indicators of potential attacks",
    "3.14.7": "Identify unauthorized use of organizational systems",
}

# ---------------------------------------------------------------------------
# 24 NIST SP 800-172 requirements selected for CMMC Level 3
# Source: 32 CFR § 170.14(c)(4) Table 1
# ---------------------------------------------------------------------------
NIST_800_172_L3 = {
    "3.1.2e":  "Restrict access to systems and system components to only those information resources that are owned, provisioned, or issued by the organization",
    "3.1.3e":  "Employ secure information transfer solutions to control information flows between security domains on connected systems",
    "3.2.1e":  "Provide awareness training focused on recognizing and responding to threats from social engineering, advanced persistent threat actors, breaches, and suspicious behaviors; update the training at least annually or when there are significant changes to the threat",
    "3.2.2e":  "Include practical exercises in awareness training for all users, tailored by roles, that are aligned with current threat scenarios and provide feedback to individuals involved in the training and their supervisors",
    "3.4.1e":  "Establish and maintain an authoritative source and repository to provide a trusted source and accountability for approved and implemented system components",
    "3.4.2e":  "Employ automated mechanisms to detect misconfigured or unauthorized system components; after detection, remove the components or place the components in a quarantine or remediation network to facilitate patching, re-configuration, or other mitigations",
    "3.4.3e":  "Employ automated discovery and management tools to maintain an up-to-date, complete, accurate, and readily available inventory of system components",
    "3.5.1e":  "Identify and authenticate systems and system components, where possible, before establishing a network connection using bidirectional authentication that is cryptographically based and replay resistant",
    "3.5.3e":  "Employ automated or manual/procedural mechanisms to prohibit system components from connecting to organizational systems unless the components are known, authenticated, in a properly configured state, or in a trust profile",
    "3.6.1e":  "Establish and maintain a security operations center capability that operates 24/7, with allowance for remote/on-call staff",
    "3.6.2e":  "Establish and maintain a cyber-incident response team that can be deployed by the organization within 24 hours",
    "3.9.2e":  "Ensure that organizational systems are protected if adverse information develops or is obtained about individuals with access to CUI",
    "3.11.1e": "Employ threat intelligence, at a minimum from open or commercial sources, and any DoD-provided sources, as part of a risk assessment to guide and inform the development of organizational systems, security architectures, selection of security solutions, monitoring, threat hunting, and response and recovery activities",
    "3.11.2e": "Conduct cyber threat hunting activities on an on-going aperiodic basis or when indications warrant, to search for indicators of compromise in organizational systems and detect, track, and disrupt threats that evade existing controls",
    "3.11.3e": "Employ advanced automation and analytics capabilities in support of analysts to predict and identify risks to organizations, systems, and system components",
    "3.11.4e": "Document or reference in the system security plan the security solution selected, the rationale for the security solution, and the risk determination",
    "3.11.5e": "Assess the effectiveness of security solutions at least annually or upon receipt of relevant cyber threat information, or in response to a relevant cyber incident, to address anticipated risk to organizational systems and the organization based on current and accumulated threat intelligence",
    "3.11.6e": "Assess, respond to, and monitor supply chain risks associated with organizational systems and system components",
    "3.11.7e": "Develop a plan for managing supply chain risks associated with organizational systems and system components; update the plan at least annually, and upon receipt of relevant cyber threat information, or in response to a relevant cyber incident",
    "3.12.1e": "Conduct penetration testing at least annually or when significant security changes are made to the system, leveraging automated scanning tools and ad hoc tests using subject matter experts",
    "3.13.4e": "Employ physical isolation techniques or logical isolation techniques or both in organizational systems and system components",
    "3.14.1e": "Verify the integrity of security critical and essential software using root of trust mechanisms or cryptographic signatures",
    "3.14.3e": "Ensure that specialized assets including IoT, IIoT, OT, GFE, Restricted Information Systems, and test equipment are included in the scope of the specified enhanced security requirements or are segregated in purpose-specific networks",
    "3.14.6e": "Use threat indicator information and effective mitigations obtained from, at a minimum, open or commercial sources, and any DoD-provided sources, to guide and inform intrusion detection and threat hunting",
}


def _family_for(ctrl):
    """Return (family_code, family_name) for a NIST control number."""
    # Handle enhanced (e.g. "3.1.2e" -> section "3.1")
    base = ctrl.rstrip("e")
    parts = base.split(".")
    section = f"{parts[0]}.{parts[1]}"
    return FAMILIES[section]


def build():
    practices = []

    # --- NIST SP 800-171 R2: 110 controls -> L1 (17) + L2 (93) ---
    for ctrl, name in sorted(NIST_800_171.items(), key=lambda x: [int(p) for p in x[0].split(".")]):
        fam_code, fam_name = _family_for(ctrl)
        level = 1 if ctrl in L1_CONTROLS else 2
        practice_id = f"{fam_code}.L{level}-{ctrl}"
        nist_ref = f"NIST SP 800-171 R2 {ctrl} \u2014 {name}"
        practices.append({
            "practice_id": practice_id,
            "name": name,
            "level": level,
            "family_code": fam_code,
            "family": fam_name,
            "nist_control": ctrl,
            "nist_ref": nist_ref,
        })

    # --- NIST SP 800-172: 24 selected controls -> L3 ---
    for ctrl, name in sorted(NIST_800_172_L3.items(), key=lambda x: [int(p) for p in x[0].rstrip("e").split(".")] + [1 if x[0].endswith("e") else 0]):
        fam_code, fam_name = _family_for(ctrl)
        practice_id = f"{fam_code}.L3-{ctrl}"
        nist_ref = f"NIST SP 800-172 {ctrl} \u2014 {name}"
        practices.append({
            "practice_id": practice_id,
            "name": name,
            "level": 3,
            "family_code": fam_code,
            "family": fam_name,
            "nist_control": ctrl,
            "nist_ref": nist_ref,
        })

    return practices


def main():
    practices = build()

    # Validate counts
    l1 = [p for p in practices if p["level"] == 1]
    l2 = [p for p in practices if p["level"] == 2]
    l3 = [p for p in practices if p["level"] == 3]
    families = sorted(set(p["family_code"] for p in practices))

    print(f"Level 1: {len(l1)} practices  (expected 17)")
    print(f"Level 2: {len(l2)} practices  (expected 93)")
    print(f"Level 3: {len(l3)} practices  (expected 24)")
    print(f"Total:   {len(practices)} practices  (expected 134)")
    print(f"Families ({len(families)}): {', '.join(families)}")

    assert len(l1) == 17, f"L1 count wrong: {len(l1)}"
    assert len(l2) == 93, f"L2 count wrong: {len(l2)}"
    assert len(l3) == 24, f"L3 count wrong: {len(l3)}"
    assert len(practices) == 134, f"Total count wrong: {len(practices)}"
    assert len(families) == 14, f"Family count wrong: {len(families)}"

    out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cmmc_data.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(practices, f, indent=2, ensure_ascii=False)
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
