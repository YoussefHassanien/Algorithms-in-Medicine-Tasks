import sys
from PyQt5 import QtCore, QtWidgets

# List to store patient data
patients = []
patient_id_counter = 1  # Counter to assign unique IDs to each patient


def add_patient(recovery, resources):
    global patient_id_counter

    if recovery is None or resources is None:
        return "Error: Recovery and Resources must not be empty.", patients

    patient = {
        "ID": patient_id_counter,
        "Recovery": int(recovery),
        "Resources": int(resources),
    }
    patients.append(patient)

    patient_id_counter += 1  # Increment the counter for the next patient

    return f"Patient {patient['ID']} added! Total patients: {len(patients)}", patients


def compute_optimal_acceptance(total_resources):
    return optimal_acceptance(patients, int(total_resources))


def optimal_acceptance(patient_data, total_resources):
    try:
        patient_recovery = [row["Recovery"] for row in patient_data]
        patient_resources = [row["Resources"] for row in patient_data]
    except KeyError:
        return "Error: Invalid input format."

    n = len(patient_recovery)

    dp = [[0] * (total_resources + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for resources in range(1, total_resources + 1):
            if resources >= patient_resources[i - 1]:
                dp[i][resources] = max(
                    dp[i - 1][resources],
                    dp[i - 1][resources - patient_resources[i - 1]]
                    + patient_recovery[i - 1],
                )
            else:
                dp[i][resources] = dp[i - 1][resources]

    accepted = []
    resources = total_resources
    for i in range(n, 0, -1):
        if (
            resources >= patient_resources[i - 1]
            and dp[i][resources]
            == dp[i - 1][resources - patient_resources[i - 1]] + patient_recovery[i - 1]
        ):
            accepted.append(f"Patient {i}")
            resources -= patient_resources[i - 1]

    accepted.reverse()

    dp_matrix = "\n".join(["\t".join(map(str, row)) for row in dp])

    return f"Accept patients: {', '.join(accepted)}\nTotal Recovery Score: {dp[n][total_resources]}\n\nDP Matrix:\n{dp_matrix}"


class PatientAcceptanceApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("🏥 Patient Acceptance Optimization System")
        self.setGeometry(100, 100, 850, 1000)
        self.setStyleSheet("background-color: #f4f4f4; font-family: 'Arial';")

        self.patients = []

        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Create a horizontal layout for the input and table sections
        top_layout = QtWidgets.QHBoxLayout()

        # Add the "Add Patient" section
        self.add_patient_section = QtWidgets.QGroupBox("✍️ Add Patient Details")
        add_patient_layout = QtWidgets.QFormLayout(self.add_patient_section)

        self.recovery_input = QtWidgets.QLineEdit()
        self.recovery_input.setPlaceholderText("Enter recovery score (1-100)")
        self.recovery_input.setStyleSheet("font-size: 24px; padding: 5px;")

        self.resources_input = QtWidgets.QLineEdit()
        self.resources_input.setPlaceholderText("Enter resources required (1-100)")
        self.resources_input.setStyleSheet("font-size: 24px; padding: 5px;")

        self.add_button = QtWidgets.QPushButton("➕ Add Patient")
        self.add_button.setStyleSheet(
            "background-color: #2196F3; color: white; font-size: 18px; padding: 10px; border-radius: 5px;"
        )
        self.add_button.clicked.connect(self.add_patient)

        self.add_message = QtWidgets.QLabel("")
        self.add_message.setStyleSheet("font-size: 18px; padding: 5px;")

        add_patient_layout.addRow("Recovery Score", self.recovery_input)
        add_patient_layout.addRow("Required Resources", self.resources_input)
        add_patient_layout.addRow(self.add_button)
        add_patient_layout.addRow(self.add_message)

        self.add_patient_section.setLayout(add_patient_layout)

        # Add the "Patient List" section with the table
        self.patient_list_section = QtWidgets.QGroupBox("📋 Patient List")
        self.patient_table = QtWidgets.QTableWidget()
        self.patient_table.setColumnCount(3)
        self.patient_table.setHorizontalHeaderLabels(["ID", "Recovery", "Resources"])
        self.patient_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.patient_table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        patient_table_layout = QtWidgets.QVBoxLayout()
        patient_table_layout.addWidget(self.patient_table)
        self.patient_list_section.setLayout(patient_table_layout)

        # Add both sections to the top layout
        top_layout.addWidget(self.add_patient_section, 1)
        top_layout.addWidget(self.patient_list_section, 2)

        layout.addLayout(top_layout)

        # Add the "Acceptance Optimization" section
        self.acceptance_section = QtWidgets.QGroupBox("📊 Acceptance Optimization")
        self.acceptance_layout = QtWidgets.QVBoxLayout(self.acceptance_section)

        self.total_resources_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.total_resources_slider.setRange(1, 50)
        self.total_resources_slider.setValue(10)
        self.total_resources_slider.valueChanged.connect(self.update_slider_value)

        self.slider_value_label = QtWidgets.QLabel(
            str(self.total_resources_slider.value())
        )
        self.slider_value_label.setStyleSheet("font-size: 18px; padding: 5px;")

        self.optimize_button = QtWidgets.QPushButton("📈 Calculate Optimal Acceptance")
        self.optimize_button.setStyleSheet(
            "background-color: #4CAF50; color: white; font-size: 18px; padding: 10px; border-radius: 5px;"
        )
        self.optimize_button.clicked.connect(self.compute_optimal_acceptance)

        self.acceptance_output = QtWidgets.QTextEdit()
        self.acceptance_output.setReadOnly(True)
        self.acceptance_output.setStyleSheet("font-size: 18px; padding: 10px;")

        self.acceptance_layout.addWidget(self.total_resources_slider)
        self.acceptance_layout.addWidget(self.slider_value_label)
        self.acceptance_layout.addWidget(self.optimize_button)
        self.acceptance_layout.addWidget(self.acceptance_output)

        layout.addWidget(self.acceptance_section)

        # Add the reset button
        self.reset_button = QtWidgets.QPushButton("🔄 Reset All")
        self.reset_button.setStyleSheet(
            "background-color: #F44336; color: white; font-size: 18px; padding: 10px; border-radius: 5px;"
        )
        self.reset_button.clicked.connect(self.reset_all)

        layout.addWidget(self.reset_button)

    def add_patient(self):
        recovery_text = self.recovery_input.text()
        resources_text = self.resources_input.text()

        if not recovery_text.isdigit() or not resources_text.isdigit():
            self.add_message.setText("Error: Enter valid numeric values.")
            return

        recovery = int(recovery_text)
        resources = int(resources_text)

        if recovery < 1 or recovery > 100 or resources < 1 or resources > 100:
            self.add_message.setText("Error: Values must be between 1 and 100.")
            return

        status, updated_patients = add_patient(recovery, resources)
        self.add_message.setText(status)

        self.patients = updated_patients
        self.update_patient_table()

        self.recovery_input.clear()
        self.resources_input.clear()

    def update_patient_table(self):
        self.patient_table.setRowCount(len(self.patients))
        for i, patient in enumerate(self.patients):
            self.patient_table.setItem(
                i, 0, QtWidgets.QTableWidgetItem(str(patient["ID"]))
            )
            self.patient_table.setItem(
                i, 1, QtWidgets.QTableWidgetItem(str(patient["Recovery"]))
            )
            self.patient_table.setItem(
                i, 2, QtWidgets.QTableWidgetItem(str(patient["Resources"]))
            )

    def update_slider_value(self):
        self.slider_value_label.setText(str(self.total_resources_slider.value()))

    def compute_optimal_acceptance(self):
        total_resources = self.total_resources_slider.value()
        acceptance_recommendations = compute_optimal_acceptance(total_resources)
        self.acceptance_output.setPlainText(acceptance_recommendations)

    def reset_all(self):
        global patient_id_counter, patients
        patient_id_counter = 1
        patients = []
        self.patients = []
        self.add_message.setText("")
        self.update_patient_table()
        self.acceptance_output.clear()
        self.recovery_input.clear()
        self.resources_input.clear()
        self.total_resources_slider.setValue(10)
        self.slider_value_label.setText("10")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = PatientAcceptanceApp()
    window.show()
    sys.exit(app.exec_())
