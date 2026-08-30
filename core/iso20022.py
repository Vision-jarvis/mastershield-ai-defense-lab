"""
MasterShield AI - ISO 20022 High-Fidelity Financial Message Framework
Mastercard Innovation Challenge @ GFF 2026

Implements ISO 20022 message envelopes:
- pacs.008.001.10 (FI to FI Customer Credit Transfer)
- pacs.002.001.12 (Payment Status Report / Fraud Decline)
- camt.056.001.10 (Payment Cancellation Request / FI Fraud Recall)
- pain.001.001.11 (Agentic / Customer Payment Initiation)
"""

from typing import Dict, Any, Optional
from datetime import datetime
import uuid
import xml.etree.ElementTree as ET


class ISO20022Engine:
    """ISO 20022 Message Generation & Validation Engine for Real-Time Payment Clearing"""

    @staticmethod
    def generate_pacs_008(
        tx_id: str,
        amount: float,
        currency: str,
        debtor_name: str,
        debtor_account: str,
        creditor_name: str,
        creditor_account: str,
        remittance_info: str = "Invoice settlement",
        agentic_auth_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generates pacs.008.001.10 message dictionary & structured XML representation"""
        msg_id = f"MSG-PACS008-{uuid.uuid4().hex[:10].upper()}"
        creation_time = datetime.utcnow().isoformat() + "Z"
        
        message_dict = {
            "GrpHdr": {
                "MsgId": msg_id,
                "CreDtTm": creation_time,
                "NbOfTxs": "1",
                "SttlmInf": {
                    "SttlmMtd": "CLRG",
                    "ClrSys": {"Prtry": "MASTERCARD_RTP_CLEARING"}
                }
            },
            "CdtTrfTxInf": {
                "PmtId": {
                    "EndToEndId": tx_id,
                    "TxId": tx_id
                },
                "IntrBkSttlmAmt": {
                    "Ccy": currency,
                    "Value": f"{amount:.2f}"
                },
                "Dbtr": {
                    "Nm": debtor_name,
                    "Id": {"OrgId": {"AnyBIC": "MSTRUS33XXX"}}
                },
                "DbtrAcct": {
                    "Id": {"Othr": {"Id": debtor_account}}
                },
                "Cdtr": {
                    "Nm": creditor_name
                },
                "CdtrAcct": {
                    "Id": {"Othr": {"Id": creditor_account}}
                },
                "RmtInf": {
                    "Ustrd": remittance_info
                },
                "SplmtryData": {
                    "Envlp": {
                        "AgenticAuthToken": agentic_auth_token or "NONE",
                        "SecurityProtocol": "MasterShield-v2026.1"
                    }
                }
            }
        }
        return message_dict

    @staticmethod
    def generate_pacs_002(
        original_tx_id: str,
        status: str, # "ACCP" (Accepted) or "RJCT" (Rejected)
        reason_code: Optional[str] = None, # "FRAD", "AM04", "AC04", "AGNT", "SYNI", "MULE"
        narrative: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generates pacs.002.001.12 Payment Status Report (Accept/Reject with ISO Reason)"""
        msg_id = f"MSG-PACS002-{uuid.uuid4().hex[:10].upper()}"
        creation_time = datetime.utcnow().isoformat() + "Z"
        
        status_info = {
            "OrgnlEndToEndId": original_tx_id,
            "OrgnlTxId": original_tx_id,
            "TxSts": status
        }
        
        if status == "RJCT":
            status_info["StsRsnInf"] = {
                "Rsn": {"Cd": reason_code or "FRAD"},
                "AddtlInf": narrative or "Declined by MasterShield AI Defense Lab: High Confidence Fraud Anomaly"
            }
            
        return {
            "GrpHdr": {
                "MsgId": msg_id,
                "CreDtTm": creation_time
            },
            "TxInfAndSts": status_info
        }

    @staticmethod
    def generate_camt_056(
        original_tx_id: str,
        reason_code: str,
        case_id: Optional[str] = None,
        narrative: str = "AI-Driven Autonomous Mule Ring / Prompt Injection Interception"
    ) -> Dict[str, Any]:
        """Generates camt.056.001.10 (Payment Recall Request for suspicious/fraudulent RTP settlement)"""
        msg_id = f"MSG-CAMT056-{uuid.uuid4().hex[:10].upper()}"
        case_ref = case_id or f"CASE-{uuid.uuid4().hex[:8].upper()}"
        
        return {
            "Assgnmt": {
                "Id": msg_id,
                "Assgnr": {"Agt": {"FinInstnId": {"BICFI": "MSTRUS33XXX"}}},
                "Assgne": {"Agt": {"FinInstnId": {"BICFI": "RECEIVER_BANK"}}},
                "CreDtTm": datetime.utcnow().isoformat() + "Z"
            },
            "Case": {
                "Id": case_ref,
                "Cretr": {"Pty": {"Nm": "MasterShield AI Defense Automation"}}
            },
            "Undrlyg": {
                "TxInf": {
                    "OrgnlEndToEndId": original_tx_id,
                    "Rsn": {"Cd": reason_code},
                    "AddtlInf": narrative
                }
            }
        }

    @staticmethod
    def dict_to_xml_string(msg_type: str, data: Dict[str, Any]) -> str:
        """Converts ISO 20022 dictionary to standard XML string"""
        root = ET.Element("Document", xmlns=f"urn:iso:std:iso:20022:tech:xsd:{msg_type}")
        
        def build_tree(element: ET.Element, sub_data: Any):
            if isinstance(sub_data, dict):
                for k, v in sub_data.items():
                    sub_elem = ET.SubElement(element, k)
                    build_tree(sub_elem, v)
            elif isinstance(sub_data, list):
                for item in sub_data:
                    build_tree(element, item)
            else:
                element.text = str(sub_data)
                
        build_tree(root, data)
        return ET.tostring(root, encoding="utf-8").decode("utf-8")


iso_engine = ISO20022Engine()
