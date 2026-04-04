"""DEMOCRAC.IA / PEIRS — Datos mock de países sin cobertura real"""

MOCK_OSINT_DATA = {
    "VEN": {
        "freedom_house_score": 16,
        "freedom_house_status": "Not Free",
        "vdem_liberal_democracy": 0.12,
        "vdem_electoral_democracy": 0.15,
        "emb_name": "Consejo Nacional Electoral (CNE)",
        "emb_independence": "compromised",
        "emb_opposition_representation": False,
        "registry_status": "no_independent_audit",
        "voter_registry_size": 21_200_000,
        "legal_framework": {
            "constitutional_amendments_recent": True,
            "opposition_party_bans": True,
            "candidate_disqualifications": 3,
            "media_law_restrictions": "severe",
        },
        "civil_liberties": {
            "freedom_of_assembly": "restricted",
            "freedom_of_press": "severely_restricted",
            "judicial_independence": "compromised",
            "political_prisoners": True,
        },
        "international_observation": {
            "invited": False,
            "restrictions": "total_ban_on_independent_observers",
        },
    },
    "NIC": {
        "freedom_house_score": 13,
        "freedom_house_status": "Not Free",
        "vdem_liberal_democracy": 0.08,
        "vdem_electoral_democracy": 0.10,
        "emb_name": "Consejo Supremo Electoral (CSE)",
        "emb_independence": "captured",
        "emb_opposition_representation": False,
        "registry_status": "no_audit",
        "voter_registry_size": 4_500_000,
        "legal_framework": {
            "constitutional_amendments_recent": True,
            "opposition_party_bans": True,
            "candidate_disqualifications": 7,
            "media_law_restrictions": "total",
        },
        "civil_liberties": {
            "freedom_of_assembly": "banned",
            "freedom_of_press": "banned",
            "judicial_independence": "captured",
            "political_prisoners": True,
        },
        "international_observation": {
            "invited": False,
            "restrictions": "all_international_ngos_expelled",
        },
    },
    "GTM": {
        "freedom_house_score": 48,
        "freedom_house_status": "Partly Free",
        "vdem_liberal_democracy": 0.41,
        "vdem_electoral_democracy": 0.48,
        "emb_name": "Tribunal Supremo Electoral (TSE)",
        "emb_independence": "partial",
        "emb_opposition_representation": True,
        "registry_status": "partially_audited",
        "voter_registry_size": 9_300_000,
        "legal_framework": {
            "constitutional_amendments_recent": False,
            "opposition_party_bans": False,
            "candidate_disqualifications": 1,
            "media_law_restrictions": "moderate",
        },
        "civil_liberties": {
            "freedom_of_assembly": "partially_restricted",
            "freedom_of_press": "partially_restricted",
            "judicial_independence": "under_pressure",
            "political_prisoners": False,
        },
        "international_observation": {
            "invited": True,
            "restrictions": "some_access_limitations",
        },
    },
    "URY": {
        "freedom_house_score": 97,
        "freedom_house_status": "Free",
        "vdem_liberal_democracy": 0.89,
        "vdem_electoral_democracy": 0.92,
        "emb_name": "Corte Electoral",
        "emb_independence": "full",
        "emb_opposition_representation": True,
        "registry_status": "fully_audited",
        "voter_registry_size": 2_700_000,
        "legal_framework": {
            "constitutional_amendments_recent": False,
            "opposition_party_bans": False,
            "candidate_disqualifications": 0,
            "media_law_restrictions": "none",
        },
        "civil_liberties": {
            "freedom_of_assembly": "guaranteed",
            "freedom_of_press": "guaranteed",
            "judicial_independence": "strong",
            "political_prisoners": False,
        },
        "international_observation": {
            "invited": True,
            "restrictions": "none",
        },
    },
}

MOCK_POLITICAL_DATA = {
    "VEN": {
        "media_bias_index": 0.78,
        "media_bias_direction": "pro_incumbent",
        "media_exposure": {
            "incumbent": 78, "opposition_a": 12, "opposition_b": 7, "others": 3,
        },
        "campaign_finance": {
            "transparency_score": 0.15,
            "state_resource_abuse": "systematic",
            "corporate_donations_disclosed": False,
        },
        "digital_ecosystem": {
            "bot_activity_detected": True,
            "bot_network_size_estimate": 45_000,
            "hate_speech_incidents": 342,
            "url_censorship_detected": True,
            "censored_domains": ["www.example-opposition-media.com"],
            "disinformation_campaigns": 12,
            "voter_suppression_tactics_online": True,
        },
        "power_network": {
            "candidate_media_ownership_links": 3,
            "state_enterprise_campaign_links": 5,
            "military_political_links": True,
        },
    },
    "NIC": {
        "media_bias_index": 0.91,
        "media_bias_direction": "pro_incumbent",
        "media_exposure": {
            "incumbent": 91, "opposition": 4, "independent": 3, "others": 2,
        },
        "campaign_finance": {
            "transparency_score": 0.05,
            "state_resource_abuse": "total",
            "corporate_donations_disclosed": False,
        },
        "digital_ecosystem": {
            "bot_activity_detected": True,
            "bot_network_size_estimate": 28_000,
            "hate_speech_incidents": 567,
            "url_censorship_detected": True,
            "censored_domains": ["confidencial.digital", "100noticias.com.ni"],
            "disinformation_campaigns": 23,
            "voter_suppression_tactics_online": True,
        },
        "power_network": {
            "candidate_media_ownership_links": 7,
            "state_enterprise_campaign_links": 12,
            "military_political_links": True,
        },
    },
    "GTM": {
        "media_bias_index": 0.42,
        "media_bias_direction": "mixed",
        "media_exposure": {
            "party_a": 38, "party_b": 32, "party_c": 18, "others": 12,
        },
        "campaign_finance": {
            "transparency_score": 0.40,
            "state_resource_abuse": "moderate",
            "corporate_donations_disclosed": True,
        },
        "digital_ecosystem": {
            "bot_activity_detected": True,
            "bot_network_size_estimate": 8_000,
            "hate_speech_incidents": 89,
            "url_censorship_detected": False,
            "censored_domains": [],
            "disinformation_campaigns": 4,
            "voter_suppression_tactics_online": False,
        },
        "power_network": {
            "candidate_media_ownership_links": 2,
            "state_enterprise_campaign_links": 1,
            "military_political_links": False,
        },
    },
    "URY": {
        "media_bias_index": 0.15,
        "media_bias_direction": "balanced",
        "media_exposure": {
            "frente_amplio": 35, "partido_nacional": 33, "partido_colorado": 20, "others": 12,
        },
        "campaign_finance": {
            "transparency_score": 0.82,
            "state_resource_abuse": "none_detected",
            "corporate_donations_disclosed": True,
        },
        "digital_ecosystem": {
            "bot_activity_detected": False,
            "bot_network_size_estimate": 0,
            "hate_speech_incidents": 12,
            "url_censorship_detected": False,
            "censored_domains": [],
            "disinformation_campaigns": 0,
            "voter_suppression_tactics_online": False,
        },
        "power_network": {
            "candidate_media_ownership_links": 0,
            "state_enterprise_campaign_links": 0,
            "military_political_links": False,
        },
    },
}

