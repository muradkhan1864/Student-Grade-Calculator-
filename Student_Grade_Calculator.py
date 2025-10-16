import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from abc import ABC, abstractmethod

# ---------------- Abstract Parent Class ----------------
class Person(ABC):
    def __init__(self, pid, name):
        self.__id = pid  # private student id
        self.__name = name  # private student name

    def get_id(self):
        return self.__id  # get id

    def get_name(self):
        return self.__name  # get name

    @abstractmethod
    def summary(self):
        pass  # abstract method (to be defined by subclass)

# ---------------- Application ----------------
class GradeCalculatorApp:
    def __init__(self, root):
        # main window setup
        self.root = root
        self.root.title("Student Grade Calculator")
        self.root.geometry("1050x700")
        self.root.config(bg="#F5F7FA")

        # data storage
        self.students = {}  # all students data
        self.editing_id = None  # id being edited
        self.editing_year = None  # year being edited

        # available years and modules
        self.year_modules = {
            "Year 1": ["Problem Solving and Programming", "Operating System", "Information Security", "Networking"],
            "Year 2": ["Computer Hardware", "Human-Computer Interaction and Web Development", "Algorithms and Data Structure", "Communications"],
            "Year 3": ["Big Data", "Internet of Things", "Contemporary Issues in Computing", "Project"]
        }

        # theme colors
        self.primary = "#4C51BF"
        self.secondary = "#667EEA"
        self.bg_color = "#F5F7FA"
        self.card_color = "#FFFFFF"
        self.text_color = "#1A202C"

        # style setup
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TLabel", background=self.bg_color, foreground=self.text_color, font=("Arial", 9, "bold"))
        style.configure("TButton", background=self.primary, foreground="white", font=("Arial", 9, "bold"), padding=4)
        style.map("TButton", background=[("active", self.secondary)])
        style.configure("Treeview.Heading", font=("Arial", 9, "bold"), background=self.primary, foreground="white")
        style.configure("Treeview", font=("Arial", 9), rowheight=20, background="white", fieldbackground="white")

        # header label
        header = tk.Label(root, text="Coventry University London (Dagenham)", bg=self.primary, fg="white",
                          font=("Arial", 13, "bold"), pady=8)
        header.pack(fill="x")

        # input section frame
        input_frame = tk.LabelFrame(root, text="Student Details", bg=self.card_color, padx=8, pady=8,
                                    font=("Arial", 9, "bold"))
        input_frame.pack(fill="x", padx=8, pady=6)

        # student id input
        ttk.Label(input_frame, text="Student ID:").grid(row=0, column=0, padx=4, pady=3, sticky="w")
        self.id_entry = ttk.Entry(input_frame, width=18)
        self.id_entry.grid(row=0, column=1, padx=4, pady=3)

        # student name input
        ttk.Label(input_frame, text="Name:").grid(row=1, column=0, padx=4, pady=3, sticky="w")
        self.name_entry = ttk.Entry(input_frame, width=18)
        self.name_entry.grid(row=1, column=1, padx=4, pady=3)

        # year selection
        ttk.Label(input_frame, text="Year:").grid(row=2, column=0, padx=4, pady=3, sticky="w")
        self.year_combobox = ttk.Combobox(input_frame, values=list(self.year_modules.keys()), state="readonly", width=40)
        self.year_combobox.current(0)
        self.year_combobox.grid(row=2, column=1, padx=4, pady=3, columnspan=2, sticky="w")
        self.year_combobox.bind("<<ComboboxSelected>>", self.show_modules)

        # frame for module marks
        self.modules_frame = tk.LabelFrame(input_frame, text="Modules & Marks", bg=self.card_color,
                                           font=("Arial", 9, "bold"), padx=8, pady=8)
        self.modules_frame.grid(row=0, column=3, rowspan=4, padx=8, pady=4)
        self.module_entries = {}
        self.show_modules()  # show modules for selected year

        # add/update and clear buttons
        tk.Button(input_frame, text="➕ Add/Update", bg=self.primary, fg="white", font=("Arial", 9, "bold"),
                  relief="flat", width=15, command=self.add_student).grid(row=0, column=4, padx=6, pady=3)
        tk.Button(input_frame, text="🧹 Clear", bg=self.secondary, fg="white", font=("Arial", 9, "bold"),
                  relief="flat", width=15, command=self.clear_inputs).grid(row=1, column=4, padx=6, pady=3)

        # table frame
        table_frame = tk.LabelFrame(root, text="Student Records", bg=self.card_color, padx=6, pady=6,
                                    font=("Arial", 9, "bold"))
        table_frame.pack(fill="both", expand=False, padx=8, pady=4)

        # columns for table
        columns = ("ID", "Name", "Year", "Modules", "Average", "Grade", "Remark", "Weighted Avg")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        for col in columns:
            self.tree.heading(col, text=col)
            width = 120
            if col == "Name": width = 180
            if col == "Modules": width = 140
            if col == "Remark": width = 160
            if col == "Weighted Avg": width = 160
            self.tree.column(col, width=width, anchor="center")

        # row colors
        self.tree.tag_configure("evenrow", background="#EEF2FF")
        self.tree.tag_configure("oddrow", background="white")

        # scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        # button row for actions
        btn_frame = tk.Frame(root, bg=self.bg_color, pady=5)
        btn_frame.pack(fill="x", padx=8, pady=4)

        # all buttons
        buttons = [
            ("📄 Report", self.show_report, self.primary),
            ("✏️ Edit", self.edit_student, self.secondary),
            ("🗑️ Delete", self.delete_student, "#E53E3E"),
            ("💾 Save CSV", self.save_to_csv, "#2F855A"),
            ("📂 Load CSV", self.load_from_csv, "#3182CE"),
            ("🔄 Reset", self.reset_all, "#38B2AC"),
            ("🌐 Overall Visualization", self.visualize_overall, "#805AD5")
        ]
        for text, cmd, color in buttons:
            tk.Button(btn_frame, text=text, bg=color, fg="white", font=("Arial", 9, "bold"),
                      relief="flat", width=16, command=cmd).pack(side="left", padx=3)

        # report section (bottom)
        report_frame = tk.LabelFrame(root, text="📊 Student Report", bg=self.card_color, padx=8, pady=8,
                                     font=("Arial", 9, "bold"))
        report_frame.pack(fill="both", expand=True, padx=8, pady=4)

        # scroll bar for report box
        report_scroll = ttk.Scrollbar(report_frame, orient="vertical")
        report_scroll.pack(side="right", fill="y")

        # text area for report
        self.report_text = tk.Text(report_frame, width=110, height=10, wrap="word", bg="#FFFFFF",
                                   fg=self.text_color, font=("Consolas", 10), relief="solid", borderwidth=1,
                                   yscrollcommand=report_scroll.set)
        report_scroll.config(command=self.report_text.yview)
        self.report_text.insert(tk.END, "Add students, then click 'Report'.")
        self.report_text.config(state="disabled")
        self.report_text.pack(fill="both", expand=True)

    # ---------------- Display modules ----------------
    def show_modules(self, event=None):
        # show modules for the selected year
        for widget in self.modules_frame.winfo_children():
            widget.destroy()
        self.module_entries.clear()
        selected_year = self.year_combobox.get()
        modules = self.year_modules.get(selected_year, [])
        for i, mod in enumerate(modules):
            ttk.Label(self.modules_frame, text=mod + ":").grid(row=i, column=0, padx=4, pady=2, sticky="w")
            entry = ttk.Entry(self.modules_frame, width=12)
            entry.grid(row=i, column=1, padx=4, pady=2)
            self.module_entries[mod] = entry

    # ---------------- Calculate grade ----------------
    def calculate_grade(self, marks):
        # calculate average and grade
        average = sum(marks)/len(marks) if marks else 0
        if any(m<40 for m in marks): return average, "F", "Fail - Resit Required"
        if average>=70: return average,"A","Excellent"
        elif average>=60: return average,"B","Very Good"
        elif average>=50: return average,"C","Good"
        elif average>=40: return average,"D","Pass"
        else: return average,"F","Fail - Resit Required"

    # ---------------- Compute weighted avg ----------------
    def compute_weighted_avg(self, record):
        # compute weighted average per year
        year_avgs = {}
        for y, data in record["year_data"].items():
            avg, _, _ = self.calculate_grade(data["marks"])
            year_avgs[y] = avg
        return year_avgs

    # ---------------- Add / Update student ----------------
    def add_student(self):
        try:
            # get input data
            sid = self.id_entry.get().strip()
            name = self.name_entry.get().strip()
            year = self.year_combobox.get()
            sid = str(sid)

            # validate id
            if not sid or not sid.isdigit():
                messagebox.showerror("Input Error","Student ID must be numeric."); return

            # validate name
            if not name or not all(c.isalpha() or c.isspace() for c in name):
                messagebox.showerror("Input Error","Name must contain only letters/spaces."); return

            # get marks
            modules = list(self.module_entries.keys())
            marks=[]
            for mod in modules:
                raw = self.module_entries[mod].get().strip()
                if raw=="": raise ValueError("Empty mark")
                val=float(raw)
                if val<0 or val>100: raise ValueError("Out of range")
                marks.append(val)
        except ValueError:
            messagebox.showerror("Input Error","Marks must be numbers between 0 and 100 for all modules."); return
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {e}"); return

        # if editing existing record
        if self.editing_id:
            record = self.students[self.editing_id]
            record["year_data"][self.editing_year]={"modules":modules,"marks":marks}
            all_marks = [m for y in record["year_data"].values() for m in y["marks"]]
            record["average"], record["grade"], record["remark"] = self.calculate_grade(all_marks)
            year_avgs = self.compute_weighted_avg(record)
            weighted_avg_text = " | ".join([f"{y}: {avg:.2f}" for y, avg in year_avgs.items()])
            for item in self.tree.get_children():
                if str(self.tree.item(item)["values"][0])==self.editing_id:
                    self.tree.item(item, values=(self.editing_id, record["name"], ", ".join(record["year_data"].keys()), len(all_marks),
                                                 f"{record['average']:.2f}", record["grade"], record["remark"], weighted_avg_text))
                    break
            self.editing_id = None
            self.editing_year = None
            messagebox.showinfo("Updated", f"Marks updated for {record['name']} ({year}).")
            self.clear_inputs()
            return

        # if student exists (adding new year)
        if sid in self.students:
            existing = self.students[sid]
            if existing["name"] != name:
                messagebox.showerror("Error", f"Student ID {sid} already exists with a different name ({existing['name']})."); return
            if year in existing["year_data"]:
                messagebox.showerror("Error", f"Student ID {sid} with Name {name} already has marks for {year}."); return

            # add new year data
            existing["year_data"][year] = {"modules": modules, "marks": marks}
            all_marks = [m for y in existing["year_data"].values() for m in y["marks"]]
            existing["average"], existing["grade"], existing["remark"] = self.calculate_grade(all_marks)
            year_avgs = self.compute_weighted_avg(existing)
            weighted_avg_text = " | ".join([f"{y}: {avg:.2f}" for y, avg in year_avgs.items()])
            for item in self.tree.get_children():
                if str(self.tree.item(item)["values"][0]) == sid:
                    self.tree.item(item, values=(sid, name, ", ".join(existing["year_data"].keys()), len(all_marks),
                                                 f"{existing['average']:.2f}", existing["grade"], existing["remark"], weighted_avg_text))
                    break
            messagebox.showinfo("Added Year", f"Added marks for {year} to student {name}.")
            self.clear_inputs()
            return

        # new student data
        avg,grade,remark=self.calculate_grade(marks)
        self.students[sid]={"name":name,"year_data":{year:{"modules":modules,"marks":marks}},"average":avg,"grade":grade,"remark":remark}
        year_avgs=self.compute_weighted_avg(self.students[sid])
        weighted_avg_text=" | ".join([f"{y}: {avg:.2f}" for y, avg in year_avgs.items()])
        tag="evenrow" if len(self.students)%2==0 else "oddrow"
        self.tree.insert("", "end", values=(sid, name, year, len(marks),
                                            f"{avg:.2f}", grade, remark, weighted_avg_text), tags=(tag,))
        self.clear_inputs()

    # ---------------- Edit student ----------------
    def edit_student(self):
        # get selected record
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a student to edit.")
            return

        sid = str(self.tree.item(selected[0])["values"][0])
        if sid not in self.students:
            messagebox.showerror("Error", f"Student ID {sid} not found.")
            return

        record = self.students[sid]
        self.editing_id = sid

        # fill form with existing data
        self.id_entry.delete(0, tk.END)
        self.id_entry.insert(0, sid)
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, record["name"])

        # populate years
        years_list = list(record["year_data"].keys())
        self.year_combobox.config(values=years_list)
        self.year_combobox.set(years_list[0])
        self.editing_year = self.year_combobox.get()

        # bind year selection
        self.year_combobox.bind("<<ComboboxSelected>>", self.on_year_select_edit)

        # show modules and marks
        self.show_modules()
        self.populate_marks_for_year(self.editing_year, record)

        messagebox.showinfo("Edit Mode", "Select the year to edit, modify marks, and click 'Add/Update'.")

    # ---------------- Year select callback ----------------
    def on_year_select_edit(self, event):
        if not self.editing_id: return
        self.editing_year=self.year_combobox.get()
        record=self.students[self.editing_id]
        self.populate_marks_for_year(self.editing_year, record)

    # ---------------- Populate marks ----------------
    def populate_marks_for_year(self, year, record):
        # show marks for selected year
        self.show_modules()
        if year not in record["year_data"]: return
        data = record["year_data"][year]
        for i, mod in enumerate(self.year_modules[year]):
            if mod in self.module_entries:
                self.module_entries[mod].delete(0, tk.END)
                self.module_entries[mod].insert(0, str(data["marks"][i]))

    # ---------------- Delete student ----------------
    def delete_student(self):
        selected=self.tree.selection()
        if not selected: messagebox.showwarning("Select","Select a student to delete."); return
        sid=str(self.tree.item(selected[0])["values"][0])
        if sid not in self.students: messagebox.showerror("Error",f"Student ID {sid} not found."); return
        confirm=messagebox.askyesno("Confirm",f"Are you sure you want to delete student ID {sid}?")
        if not confirm: return
        del self.students[sid]
        self.tree.delete(selected[0])
        messagebox.showinfo("Deleted", f"Student ID {sid} deleted.")

    # ---------------- Clear inputs ----------------
    def clear_inputs(self):
        # clear all input fields
        self.id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        for e in self.module_entries.values():
            e.delete(0, tk.END)
        self.year_combobox.config(values=list(self.year_modules.keys()))
        self.year_combobox.current(0)
        self.show_modules()
        self.editing_id=None
        self.editing_year=None

    # ---------------- Show report ----------------
    def show_report(self):
        # generate student report
        if not self.students: messagebox.showwarning("No Data","No students added yet."); return
        self.report_text.config(state="normal")
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END,"----- 📊 Student Grade Report -----\n\n")
        for sid,s in self.students.items():
            all_marks = [m for y in s["year_data"].values() for m in y["marks"]]
            overall_avg, overall_grade, overall_remark = self.calculate_grade(all_marks)
            for y,data in s["year_data"].items():
                mods=", ".join(f"{m}:{mark}" for m, mark in zip(data["modules"],data["marks"]))
                self.report_text.insert(tk.END,f"ID:{sid} | Name:{s['name']} | Year:{y}\nModules:{mods}\n\n")
            self.report_text.insert(tk.END,f"Overall Average:{overall_avg:.2f} | Grade:{overall_grade} ({overall_remark})\n")
            self.report_text.insert(tk.END,"-------------------------------------------\n\n")
        self.report_text.config(state="disabled")

    # ---------------- Reset ----------------
    def reset_all(self):
        # clear all data
        self.students.clear()
        self.tree.delete(*self.tree.get_children())
        self.report_text.config(state="normal")
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END,"Add students, then click 'Report'.")
        self.report_text.config(state="disabled")
        self.editing_id=None
        self.editing_year=None

    # ---------------- Save CSV ----------------
    def save_to_csv(self):
        # save all student data to csv file
        if not self.students: messagebox.showwarning("No Data","No student data to save."); return
        file_path=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV files","*.csv")])
        if not file_path: return
        try:
            with open(file_path,"w",newline="",encoding="utf-8") as f:
                writer=csv.writer(f)
                writer.writerow(["ID","Name","Year_Data","Average","Grade","Remark"])
                for sid,s in self.students.items():
                    year_data_str=";".join([f"{y}:{'|'.join(data['modules'])}:{'|'.join(map(str,data['marks']))}" for y,data in s["year_data"].items()])
                    writer.writerow([sid,s["name"],year_data_str,f"{s['average']:.2f}",s["grade"],s["remark"]])
            messagebox.showinfo("Saved",f"Data saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error",f"Failed to save file: {e}")

    # ---------------- Load CSV ----------------
    def load_from_csv(self):
        # load student data from csv file
        file_path=filedialog.askopenfilename(filetypes=[("CSV files","*.csv")])
        if not file_path: return
        try:
            with open(file_path,"r",encoding="utf-8") as f:
                reader=csv.DictReader(f)
                self.students.clear()
                for row in reader:
                    year_data={}
                    for ydata in row["Year_Data"].split(";"):
                        if not ydata: continue
                        y,m_str,marks_str=ydata.split(":")
                        year_data[y]={"modules":m_str.split("|"),"marks":list(map(float,marks_str.split("|")))}
                    self.students[row["ID"]]={"name":row["Name"],"year_data":year_data,"average":float(row["Average"]),"grade":row["Grade"],"remark":row["Remark"]}
            self.tree.delete(*self.tree.get_children())
            for i,(sid,s) in enumerate(self.students.items()):
                tag="evenrow" if i%2==0 else "oddrow"
                year_avgs=self.compute_weighted_avg(s)
                weighted_avg_text=" | ".join([f"{y}: {avg:.2f}" for y,avg in year_avgs.items()])
                self.tree.insert("", "end", values=(sid,s["name"],", ".join(s["year_data"].keys()), sum(len(d['marks']) for d in s['year_data'].values()),
                                                    f"{s['average']:.2f}", s["grade"], s["remark"], weighted_avg_text), tags=(tag,))
            messagebox.showinfo("Loaded",f"Data loaded from {file_path}")
        except Exception as e:
            messagebox.showerror("Error",f"Failed to load file: {e}")

          # ---------------- Visualization ----------------
    def visualize_overall(self):
        import pandas as pd
        import matplotlib.pyplot as plt

        if not self.students:
            messagebox.showwarning("No Data", "No student data to visualize.")
            return

        # Prepare data
        data = []
        for sid, s in self.students.items():
            data.append({
                "ID": sid,
                "Name": s["name"],
                "Average": s["average"],
                "Grade": s["grade"]
            })
        df = pd.DataFrame(data)

        # Grade distribution (pie chart)
        grade_counts = df["Grade"].value_counts()
        plt.figure(figsize=(10, 4))

        plt.subplot(1, 2, 1)
        plt.pie(grade_counts, labels=grade_counts.index, autopct="%1.1f%%", startangle=140)
        plt.title("Grade Distribution")

        # Average marks (bar chart)
        plt.subplot(1, 2, 2)
        plt.bar(df["Name"], df["Average"])
        plt.xticks(rotation=45, ha="right")
        plt.title("Average Marks per Student")
        plt.ylabel("Average (%)")
        plt.tight_layout()

        plt.show()
# ---------------- Run ----------------
if __name__=="__main__":
    # create main window and run app
    root=tk.Tk()
    app=GradeCalculatorApp(root)
    root.mainloop()

