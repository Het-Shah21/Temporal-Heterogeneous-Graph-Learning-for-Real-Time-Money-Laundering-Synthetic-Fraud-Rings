import { DatasetPreset } from "@/types/fraud";

export const IBM_DATASET_PRESETS: DatasetPreset[] = [
  {
    id: "aml_wire_alert",
    title: "IBM AML High-Risk Wire Outflow (Alert)",
    type: "ALERT_LAUNDERING",
    description: "Rapid high-value wire cross-bank from an active high-outflow hub (83 historical outgoing edges).",
    particulars: {
      Timestamp: "2022/09/01 14:30:00",
      From_Bank: "010",
      From_Account: "800E8B7F0",
      To_Bank: "022",
      To_Account: "8123FB9B0",
      Amount_Received: 145000.00,
      Receiving_Currency: "US Dollar",
      Payment_Format: "Wire"
    }
  },
  {
    id: "aml_structuring_cash",
    title: "IBM AML Cash Structuring Smurf (Alert)",
    type: "ALERT_LAUNDERING",
    description: "Sub-$10k deposit ($9,950) executed via cash format to evade mandatory CTR threshold reporting.",
    particulars: {
      Timestamp: "2022/09/01 03:15:00",
      From_Bank: "001",
      From_Account: "8059FB490",
      To_Bank: "025",
      To_Account: "801832F80",
      Amount_Received: 9950.00,
      Receiving_Currency: "US Dollar",
      Payment_Format: "Cash"
    }
  },
  {
    id: "aml_ach_normal",
    title: "IBM AML Standard Intra-Bank Transfer (Normal)",
    type: "NORMAL_LEGITIMATE",
    description: "Routine low-value ACH settlement between two established accounts within the same domestic bank.",
    particulars: {
      Timestamp: "2022/09/01 09:00:00",
      From_Bank: "010",
      From_Account: "800D4E490",
      To_Bank: "010",
      To_Account: "8140A8A71",
      Amount_Received: 45.00,
      Receiving_Currency: "US Dollar",
      Payment_Format: "ACH"
    }
  },
  {
    id: "aml_cheque_normal",
    title: "IBM AML Standard Cheque Settlement (Normal)",
    type: "NORMAL_LEGITIMATE",
    description: "Verified daylight retail cheque settlement consistent with historical account baseline.",
    particulars: {
      Timestamp: "2022/09/01 11:45:00",
      From_Bank: "014",
      From_Account: "8095AF7C0",
      To_Bank: "014",
      To_Account: "800C71170",
      Amount_Received: 1250.00,
      Receiving_Currency: "US Dollar",
      Payment_Format: "Cheque"
    }
  }
];
