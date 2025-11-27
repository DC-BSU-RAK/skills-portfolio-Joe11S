import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import json
import os
import pathlib
from functools import reduce

# --- Student and Data Repository ---

class Student:
    """Represents a single student record and handles calculations."""
    MAX_COURSEWORK = 20 * 3  # 60 marks
    MAX_EXAM = 100
    MAX_TOTAL = MAX_COURSEWORK + MAX_EXAM # 160 marks

    def __init__(self, code, name, coursework_marks, exam_mark):
        self.code = str(code)
        self.name = name
        self.coursework_marks = [int(m) for m in coursework_marks] 
        self.exam_mark = int(exam_mark)
        self.total_coursework = sum(self.coursework_marks)
        self.total_score = self.total_coursework + self.exam_mark
        self.overall_percentage = (self.total_score / self.MAX_TOTAL) * 100
        self.grade = self._calculate_grade()

    def _calculate_grade(self):
        perc = self.overall_percentage
        if perc >= 70: return 'A'
        elif perc >= 60: return 'B'
        elif perc >= 50: return 'C'
        elif perc >= 40: return 'D'
        else: return 'F'

    def get_display_data(self):
        return (
            f"Name: {self.name}\n"
            f"Student Number: {self.code}\n"
            f"Total Coursework Mark: {self.total_coursework} / {self.MAX_COURSEWORK}\n"
            f"Exam Mark: {self.exam_mark} / {self.MAX_EXAM}\n"
            f"Overall Percentage: {self.overall_percentage:.2f}%\n"
            f"Student Grade: {self.grade}\n"
            f"{'-' * 40}"
        )
    
    def to_dict(self):
        return {
            "code": self.code,
            "name": self.name,
            "coursework_marks": self.coursework_marks,
            "exam_mark": self.exam_mark
        }

class DataRepository:
    """Handles loading and persistence of student data using JSON files."""
    DATA_FOLDER = "Assessment 1 - Skills Portfolio/03-StudentRecord/data" 

    def __init__(self):
        pathlib.Path(self.DATA_FOLDER).mkdir(exist_ok=True)
        self.students = self._load_data()

    def _load_data(self):
        students = []
        for filename in os.listdir(self.DATA_FOLDER):
            if filename.endswith(".json"):
                filepath = os.path.join(self.DATA_FOLDER, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        student = Student(
                            code=data['code'],
                            name=data['name'],
                            coursework_marks=data['coursework_marks'],
                            exam_mark=data['exam_mark']
                        )
                        students.append(student)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        return students

    def save_student(self, student, original_name=None):
        new_filepath = os.path.join(self.DATA_FOLDER, f"{student.name}.json")
        
        if original_name and original_name != student.name:
            old_filepath = os.path.join(self.DATA_FOLDER, f"{original_name}.json")
            if os.path.exists(old_filepath):
                try:
                    os.remove(old_filepath)
                except Exception as e:
                    messagebox.showerror("Rename Error", f"Could not delete old file ({original_name}.json): {e}")
                    return False

        try:
            if not original_name and os.path.exists(new_filepath):
                 if not messagebox.askyesno("Confirm Overwrite", 
                                             f"A record for '{student.name}' already exists. Overwrite?"):
                    return False
                    
            with open(new_filepath, 'w') as f:
                json.dump(student.to_dict(), f, indent=4)
            return True
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save data for {student.name}: {e}")
            return False
            
    def delete_student(self, student_name):
        filepath = os.path.join(self.DATA_FOLDER, f"{student_name}.json")
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                return True
            except Exception as e:
                messagebox.showerror("Delete Error", f"Could not delete file for {student_name}: {e}")
                return False
        return False

# --- Application ---

class StudentApp(tk.Tk):
    """The main Tkinter GUI application."""
    def __init__(self):
        super().__init__()
        self.title("🎓 Student Manager (CRUD & Sorting Enabled)")
        self.geometry("700x550")
        
        # Track the current sort state for the Treeview
        self.sort_column = 'name'
        self.sort_reverse = False
        
        # Load the data via the repository
        self.repository = DataRepository()
        self.students = self.repository.students
            
        if not self.students:
            messagebox.showwarning("No Data", f"No student data was loaded. Check the '{self.repository.DATA_FOLDER}' folder.")
            
        self._create_widgets()
        self._create_menu()

    def _create_widgets(self):
        """Sets up the main display area using a Treeview for the table."""
        
        # --- Top Frame: Filter Bar ---
        top_frame = tk.Frame(self)
        top_frame.pack(fill='x', padx=10, pady=(5, 0))
        tk.Label(top_frame, text="Filter by Name/Code:", anchor='w').pack(side=tk.LEFT)
        
        self.filter_var = tk.StringVar()
        self.filter_var.trace_add("write", lambda name, index, mode: self._filter_student_list(self.filter_var.get()))
        self.filter_entry = tk.Entry(top_frame, textvariable=self.filter_var)
        self.filter_entry.pack(side=tk.LEFT, fill='x', expand=True, padx=(5, 0))
        
        # --- Middle Frame: Treeview Table (Main Display) ---
        
        tree_frame = tk.Frame(self)
        tree_frame.pack(fill='both', expand=False, padx=10, pady=(5, 5))
        
        # Define Columns for the Treeview
        self.columns = ('code', 'name', 'coursework_total', 'exam_mark', 'overall_perc', 'grade')
        self.student_tree = ttk.Treeview(tree_frame, columns=self.columns, show='headings', height=10)

        # Configure Headings and Column Widths
        self.student_tree.heading('code', text='Code', anchor=tk.W)
        self.student_tree.heading('name', text='Name', anchor=tk.W)
        self.student_tree.heading('coursework_total', text='CW Total (Max 60)', anchor=tk.CENTER)
        self.student_tree.heading('exam_mark', text='Exam (Max 100)', anchor=tk.CENTER)
        self.student_tree.heading('overall_perc', text='Overall % (Base 160)', anchor=tk.CENTER)
        self.student_tree.heading('grade', text='Grade', anchor=tk.CENTER)

        self.student_tree.column('code', width=80, anchor=tk.W, stretch=tk.NO)
        self.student_tree.column('name', width=180, anchor=tk.W)
        self.student_tree.column('coursework_total', width=100, anchor=tk.CENTER, stretch=tk.NO)
        self.student_tree.column('exam_mark', width=80, anchor=tk.CENTER, stretch=tk.NO)
        self.student_tree.column('overall_perc', width=120, anchor=tk.CENTER, stretch=tk.NO)
        self.student_tree.column('grade', width=70, anchor=tk.CENTER, stretch=tk.NO)
        
        # Add Scrollbar
        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.student_tree.yview)
        tree_scroll.pack(side='right', fill='y')
        self.student_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.student_tree.pack(side='left', fill='both', expand=True)
        
        # Bind Selection and Sorting Events
        self.student_tree.bind('<<TreeviewSelect>>', self._on_treeview_select)
        
        # BINDING FOR COLUMN SORTING
        for col in self.columns:
            self.student_tree.heading(col, command=lambda c=col: self._sort_column(c))
        
        # --- Bottom Frame: Detailed Output Area ---
        tk.Label(self, text="Detailed Record Output:", anchor='w').pack(fill='x', padx=10, pady=(5, 0))
        self.display_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, font=("Consolas", 10), 
                                                     bg="#f0f0f0", fg="#333333", height=10)
        self.display_area.pack(expand=True, fill="both", padx=10, pady=10)
        self.display_area.config(state=tk.DISABLED)
        
        # Populate the table on startup (Initial sort by name ascending)
        self._populate_treeview(self.students)
        self._update_display("Welcome to the Student Manager.\nSelect a row in the table above to view the detailed record.")

    def _create_menu(self):
        """Creates the main menubar with required options and a new Edit menu."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Actions Menu (Original Requirements 1, 3, 4)
        actions_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Actions", menu=actions_menu)

        actions_menu.add_command(label="View All Student Records", command=self._view_all_records)
        actions_menu.add_separator()
        actions_menu.add_command(label="Show Highest Scorer", command=self._show_highest_scorer)
        actions_menu.add_command(label="Show Lowest Scorer", command=self._show_lowest_scorer)
        
        # Edit Menu (CRUD Operations)
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Add Record", command=lambda: self._data_entry_dialog(mode='Add'))
        edit_menu.add_command(label="Edit Record", command=self._edit_selected_record)
        edit_menu.add_command(label="Delete Record", command=self._delete_selected_student)

        menubar.add_command(label="Exit", command=self.quit)
        
    def _sort_column(self, col):
        """Handles the logic for sorting the Treeview by the selected column."""
        
        # 1. Determine sort direction
        # If the same column is clicked, toggle the direction
        if col == self.sort_column:
            self.sort_reverse = not self.sort_reverse
        else:
            # If a new column is clicked, set the new column and default to ascending (False)
            self.sort_column = col
            self.sort_reverse = False
            
        # 2. Get the items and sort them
        data = [(self.student_tree.set(k, col), k) for k in self.student_tree.get_children('')]
        
        # Determine the key conversion based on the column type for accurate sorting
        if col in ('code', 'coursework_total', 'exam_mark'):
            data.sort(key=lambda t: int(t[0]), reverse=self.sort_reverse)
        elif col in ('overall_perc'):
            # Strip the '%' and convert to float
            data.sort(key=lambda t: float(t[0].strip('%')), reverse=self.sort_reverse)
        else: # Default: sort by string (name, grade)
            data.sort(key=lambda t: t[0].lower(), reverse=self.sort_reverse)

        # 3. Rearrange the items in the Treeview
        for index, (val, k) in enumerate(data):
            self.student_tree.move(k, '', index)

        # 4. Update the heading visual indicator (optional but helpful)
        for c in self.columns:
            self.student_tree.heading(c, text=self.student_tree.heading(c, 'text').replace(' ▲', '').replace(' ▼', ''))
        
        arrow = ' ▼' if self.sort_reverse else ' ▲'
        current_text = self.student_tree.heading(col, 'text')
        self.student_tree.heading(col, text=current_text + arrow)


    def _populate_treeview(self, student_list):
        """Fills the Treeview widget with student data."""
        # Clear existing data
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)

        # Sort students initially by name before populating the Treeview
        sorted_students = sorted(student_list, key=lambda s: s.name)
        
        for student in sorted_students:
            # Insert the student data into the table
            self.student_tree.insert('', tk.END, 
                                     iid=student.code, # Use the unique code as the item identifier (iid)
                                     values=(
                                         student.code, 
                                         student.name, 
                                         student.total_coursework, 
                                         student.exam_mark, 
                                         f"{student.overall_percentage:.2f}%",
                                         student.grade
                                     ))
        
        # Reapply current sort state if it exists (e.g., after filter/reload)
        if self.students:
            self._sort_column(self.sort_column)


    # --- Utility and Display Methods (CRUD and Menu Handlers remain the same) ---
    # (The rest of the class methods, including _filter_student_list, _on_treeview_select, 
    # _validate_marks, _data_entry_dialog, _edit_selected_record, _delete_selected_student, 
    # and the Menu Handlers, remain the same as the previous full working solution.)
    
    # ... (Rest of the StudentApp class code below) ...
    
    def _filter_student_list(self, filter_text):
        """Filters the Treeview based on text input (implements the interactive search)."""
        search_term = filter_text.lower()
        
        if not search_term:
            filtered_students = self.students
        else:
            # Search across name and code
            filtered_students = [
                s for s in self.students 
                if search_term in s.name.lower() or search_term in s.code
            ]
            
        self._populate_treeview(filtered_students)


    def _on_treeview_select(self, event):
        """Handles Treeview selection (implements Menu Item 2: View individual student record)."""
        selected_item = self.student_tree.focus()
        if not selected_item:
            return

        student_code = selected_item
        
        try:
            student = next(s for s in self.students if s.code == student_code)
            
            output = f"## Individual Student Record (Selected)\n\n"
            output += student.get_display_data()
            self._update_display(output)
            
        except StopIteration:
            self._update_display(f"Error: Could not find student with code {student_code}.")

    def _update_display(self, content):
        """Clears and updates the ScrolledText display."""
        self.display_area.config(state=tk.NORMAL)
        self.display_area.delete('1.0', tk.END)
        self.display_area.insert(tk.END, content)
        self.display_area.config(state=tk.DISABLED)
        
    # --- Data Management (CRUD) Implementation ---

    def _get_selected_student(self):
        """Retrieves the Student object selected in the Treeview."""
        selected_item = self.student_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a student from the table first.")
            return None
        
        student_code = selected_item
        try:
            return next(s for s in self.students if s.code == student_code)
        except StopIteration:
            messagebox.showerror("Error", "Selected student record not found in memory.")
            return None

    def _validate_marks(self, marks, mode, original_code=None):
        """Helper to validate data input."""
        try:
            if not marks['code'].strip() or not marks['name'].strip():
                messagebox.showerror("Input Error", "Student Code and Name cannot be empty.")
                return False
            
            code = str(marks['code'])
            if not (1000 <= int(code) <= 9999):
                 messagebox.showerror("Input Error", "Student Code must be between 1000 and 9999.")
                 return False

            if mode == 'Add' or (mode == 'Edit' and code != original_code):
                if any(s.code == code for s in self.students):
                    messagebox.showerror("Input Error", f"Student code {code} already exists.")
                    return False

            cw1 = int(marks['cw1']); cw2 = int(marks['cw2']); cw3 = int(marks['cw3'])
            exam = int(marks['exam'])
            
            if not (0 <= cw1 <= 20 and 0 <= cw2 <= 20 and 0 <= cw3 <= 20):
                messagebox.showerror("Input Error", "Coursework marks must be between 0 and 20.")
                return False
                
            if not (0 <= exam <= 100):
                messagebox.showerror("Input Error", "Exam mark must be between 0 and 100.")
                return False
            
            return True
        except ValueError:
            messagebox.showerror("Input Error", "Marks and Code must be valid numbers.")
            return False

    def _data_entry_dialog(self, mode='Add', student_data=None):
        """Opens a dialog window for adding or editing student data."""
        dialog = tk.Toplevel(self)
        dialog.title(f"{mode} Student Record")
        dialog.geometry("350x350")
        dialog.transient(self) 
        dialog.grab_set() 
        
        original_student_index = -1
        original_name = None
        original_code = None
        
        if mode == 'Edit' and student_data:
            original_name = student_data.name
            original_code = student_data.code
            try:
                original_student_index = self.students.index(student_data)
            except ValueError:
                pass 

        input_fields = [
            ("Student Code (1000-9999):", "code", original_code if mode == 'Edit' else ""),
            ("Name:", "name", original_name if mode == 'Edit' else ""),
            ("Coursework 1 (Max 20):", "cw1", student_data.coursework_marks[0] if mode == 'Edit' else ""),
            ("Coursework 2 (Max 20):", "cw2", student_data.coursework_marks[1] if mode == 'Edit' else ""),
            ("Coursework 3 (Max 20):", "cw3", student_data.coursework_marks[2] if mode == 'Edit' else ""),
            ("Exam Mark (Max 100):", "exam", student_data.exam_mark if mode == 'Edit' else "")
        ]
        entries = {}
        
        # Create labels and entry fields
        for i, (label_text, key, default_value) in enumerate(input_fields):
            tk.Label(dialog, text=label_text, anchor='w').grid(row=i, column=0, padx=5, pady=5, sticky='w')
            entry = tk.Entry(dialog)
            entry.insert(0, default_value)
            
            if mode == 'Edit' and key == 'code':
                entry.config(state=tk.DISABLED) 
            entry.grid(row=i, column=1, padx=5, pady=5, sticky='ew')
            entries[key] = entry

        def save_record():
            """Gathers data, validates it, saves the JSON, and updates the GUI."""
            marks = {key: entry.get() for key, entry in entries.items()}
            
            if mode == 'Edit':
                marks['code'] = original_code

            if not self._validate_marks(marks, mode, original_code):
                return
            
            try:
                temp_student = Student(
                    code=marks['code'],
                    name=marks['name'],
                    coursework_marks=[marks['cw1'], marks['cw2'], marks['cw3']],
                    exam_mark=marks['exam']
                )

                if self.repository.save_student(temp_student, original_name=original_name):
                    
                    if mode == 'Add':
                        self.students.append(temp_student)
                        msg = f"Successfully added and saved: {temp_student.name}"
                    
                    elif mode == 'Edit':
                        self.students[original_student_index] = temp_student
                        msg = f"Successfully updated and saved: {temp_student.name}"
                        
                    self._populate_treeview(self.students) # Full refresh to include sort changes
                    self._update_display(msg)
                    dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process student: {e}")

        tk.Button(dialog, text=f"Save Record", command=save_record, bg="green", fg="white").grid(
            row=len(input_fields), column=0, columnspan=2, pady=10)
        dialog.columnconfigure(1, weight=1) 

    def _edit_selected_record(self):
        """Prepares data for the _data_entry_dialog in Edit mode."""
        student_to_edit = self._get_selected_student()
        if student_to_edit:
            self._data_entry_dialog(mode='Edit', student_data=student_to_edit)

    def _delete_selected_student(self):
        """Deletes the selected student record from the GUI and filesystem."""
        student_to_delete = self._get_selected_student()
        if not student_to_delete:
            return 

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to permanently delete the record for:\n\n{student_to_delete.name} (Code: {student_to_delete.code})?"
        )
        
        if confirm:
            if self.repository.delete_student(student_to_delete.name):
                self.students.remove(student_to_delete)
                self.student_tree.delete(student_to_delete.code)
                self._update_display(f"✅ Successfully deleted record for: {student_to_delete.name}")

    def _view_all_records(self):
        """Handles Menu Item 1: View all student records."""
        self.students = self.repository._load_data()
        self._populate_treeview(self.students) 
        
        output = "All Student Records\n\n"
        total_percentage = reduce(lambda acc, s: acc + s.overall_percentage, self.students, 0)
        
        for student in self.students:
            output += student.get_display_data() + "\n"
            
        num_students = len(self.students)
        avg_percentage = total_percentage / num_students if num_students > 0 else 0
        
        output += f"## Class Summary\n"
        output += f"Total Number of Students: {num_students}\n"
        output += f"Average Overall Percentage Mark: {avg_percentage:.2f}%\n"
        
        self._update_display(output)

    def _show_highest_scorer(self):
        """Handles Menu Item 3: Show student with highest total score."""
        if not self.students: return

        highest_scorer = max(self.students, key=lambda s: s.total_score)
        output = "## 3. Student with Highest Total Score\n\n"
        output += f"🥇 **Highest Score Achieved: {highest_scorer.total_score} / {Student.MAX_TOTAL}**\n\n"
        output += highest_scorer.get_display_data()
        self._update_display(output)
        
        self.student_tree.selection_set(highest_scorer.code)
        self.student_tree.focus(highest_scorer.code)


    def _show_lowest_scorer(self):
        """Handles Menu Item 4: Show student with lowest total score."""
        if not self.students: return

        lowest_scorer = min(self.students, key=lambda s: s.total_score)
        output = "## 4. Student with Lowest Total Score\n\n"
        output += f"⬇️ **Lowest Score Achieved: {lowest_scorer.total_score} / {Student.MAX_TOTAL}**\n\n"
        output += lowest_scorer.get_display_data()
        self._update_display(output)

        self.student_tree.selection_set(lowest_scorer.code)
        self.student_tree.focus(lowest_scorer.code)

# Run App
if __name__ == "__main__":
    app = StudentApp()
    if app.winfo_exists():
        app.mainloop()