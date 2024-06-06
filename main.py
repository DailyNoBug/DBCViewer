import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cantools
import pandas as pd


class DBCEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("DBC Editor")
        self.root.geometry("1000x600")

        # Configure style
        style = ttk.Style()
        style.theme_use('clam')  # Use 'clam' theme as a base
        style.configure("TButton", padding=6, relief="flat", background="#007ACC", foreground="#FFFFFF")
        style.configure("TFrame", background="#2B2B2B")
        style.configure("TLabel", background="#2B2B2B", foreground="#FFFFFF")
        style.configure("Treeview", background="#3C3F41", foreground="#FFFFFF", fieldbackground="#3C3F41")
        style.map("TButton", background=[("active", "#005F8A")])

        # Frame for buttons
        button_frame = ttk.Frame(root)
        button_frame.pack(fill=tk.X, pady=5)

        self.load_button = ttk.Button(button_frame, text="Load DBC File", command=self.load_dbc)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.save_button = ttk.Button(button_frame, text="Save DBC File", command=self.save_dbc, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.add_button = ttk.Button(button_frame, text="Add Signal", command=self.add_signal, state=tk.DISABLED)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = ttk.Button(button_frame, text="Delete Signal", command=self.delete_signal,
                                        state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        self.tree = ttk.Treeview(root, columns=("Message Name", "Message ID", "Signal Name", "Start Bit", "Length",
                                                "Byte Order", "Is Signed", "Scale", "Offset", "Minimum", "Maximum",
                                                "Unit"), show='headings')
        self.tree.pack(fill=tk.BOTH, expand=1)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)

        self.tree.bind('<Double-1>', self.on_item_double_click)
        self.tree.bind('<Button-3>', self.show_context_menu)

        # Create context menu
        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_signal)

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def copy_signal(self):
        selected_item = self.tree.selection()[0]
        values = self.tree.item(selected_item, "values")
        new_values = list(values)
        new_values[0] += "_copy"  # Change the name to indicate it's a copy
        self.tree.insert("", "end", values=new_values)
        new_series = pd.Series(new_values, index=self.df.columns)
        self.df = pd.concat([self.df, new_series.to_frame().T], ignore_index=True)

    def load_dbc(self):
        file_path = filedialog.askopenfilename(filetypes=[("DBC Files", "*.dbc")])
        if file_path:
            try:
                self.db = cantools.database.load_file(file_path)
                self.display_dbc_info()
                self.save_button.config(state=tk.NORMAL)
                self.add_button.config(state=tk.NORMAL)
                self.delete_button.config(state=tk.NORMAL)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load DBC file: {e}")

    def display_dbc_info(self):
        self.tree.delete(*self.tree.get_children())
        data = []
        for message in self.db.messages:
            for signal in message.signals:
                data.append((message.name, message.frame_id, signal.name, signal.start, signal.length,
                             signal.byte_order, signal.is_signed, signal.scale, signal.offset,
                             signal.minimum, signal.maximum, signal.unit))

        for row in data:
            self.tree.insert("", "end", values=row)

        self.df = pd.DataFrame(data, columns=["Message Name", "Message ID", "Signal Name", "Start Bit", "Length",
                                              "Byte Order", "Is Signed", "Scale", "Offset", "Minimum", "Maximum",
                                              "Unit"])
        # Ensure proper data types
        self.df["Message ID"] = self.df["Message ID"].astype(int)
        self.df["Start Bit"] = self.df["Start Bit"].astype(int)
        self.df["Length"] = self.df["Length"].astype(int)
        self.df["Is Signed"] = self.df["Is Signed"].astype(bool)
        self.df["Scale"] = self.df["Scale"].astype(float)
        self.df["Offset"] = self.df["Offset"].astype(float)
        self.df["Minimum"] = self.df["Minimum"].astype(float)
        self.df["Maximum"] = self.df["Maximum"].astype(float)

    def on_item_double_click(self, event):
        item = self.tree.selection()[0]
        values = self.tree.item(item, "values")

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Signal")
        edit_window.configure(background="#2B2B2B")
        entries = []
        labels = ["Message Name", "Message ID", "Signal Name", "Start Bit", "Length", "Byte Order", "Is Signed",
                  "Scale", "Offset", "Minimum", "Maximum", "Unit"]

        for i, label in enumerate(labels):
            ttk.Label(edit_window, text=label).grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(edit_window)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entry.insert(0, values[i])
            entries.append(entry)

        def save_changes():
            new_values = [entry.get() for entry in entries]
            self.tree.item(item, values=new_values)
            for i, col in enumerate(self.df.columns):
                new_val = new_values[i]
                if col in ["Message ID", "Start Bit", "Length"]:
                    new_val = int(new_val)
                elif col in ["Is Signed"]:
                    new_val = new_val.lower() in ["true", "1", "yes"]
                elif col in ["Scale", "Offset", "Minimum", "Maximum"]:
                    new_val = float(new_val)
                self.df.at[
                    self.df[(self.df["Message Name"] == values[0]) & (self.df["Signal Name"] == values[2])].index[
                        0], col] = new_val
            edit_window.destroy()

        save_button = ttk.Button(edit_window, text="Save", command=save_changes)
        save_button.grid(row=len(labels), columnspan=2, pady=5)

    def add_signal(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Signal")
        add_window.configure(background="#2B2B2B")
        entries = []
        labels = ["Message Name", "Message ID", "Signal Name", "Start Bit", "Length", "Byte Order", "Is Signed",
                  "Scale", "Offset", "Minimum", "Maximum", "Unit"]

        for i, label in enumerate(labels):
            ttk.Label(add_window, text=label).grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(add_window)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries.append(entry)

        def add_new_signal():
            new_values = [entry.get() for entry in entries]
            self.tree.insert("", "end", values=new_values)
            new_series = pd.Series(new_values, index=self.df.columns)
            self.df = pd.concat([self.df, new_series.to_frame().T], ignore_index=True)
            add_window.destroy()

        add_button = ttk.Button(add_window, text="Add", command=add_new_signal)
        add_button.grid(row=len(labels), columnspan=2, pady=5)

    def delete_signal(self):
        selected_item = self.tree.selection()[0]
        values = self.tree.item(selected_item, "values")
        self.tree.delete(selected_item)
        self.df = self.df.drop(
            self.df[(self.df["Message Name"] == values[0]) & (self.df["Signal Name"] == values[2])].index)

    def save_dbc(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".dbc", filetypes=[("DBC Files", "*.dbc")])
        if file_path:
            try:
                new_db = cantools.database.Database()
                messages = {}

                for _, row in self.df.iterrows():
                    if row["Message Name"] not in messages:
                        message = cantools.database.Message(frame_id=int(row["Message ID"]), name=row["Message Name"],
                                                            length=8, signals=[])
                        messages[row["Message Name"]] = message
                        new_db.messages.append(message)

                    byte_order = 0 if row["Byte Order"].lower() == 'little_endian' else 1
                    signal = cantools.database.Signal(name=row["Signal Name"], start=int(row["Start Bit"]),
                                                      length=int(row["Length"]),
                                                      byte_order=byte_order, is_signed=bool(row["Is Signed"]),
                                                      unit=row["Unit"])
                    signal.scale = float(row["Scale"])
                    signal.offset = float(row["Offset"])
                    signal.minimum = float(row["Minimum"])
                    signal.maximum = float(row["Maximum"])

                    messages[row["Message Name"]].signals.append(signal)

                with open(file_path, 'w') as f:
                    f.write(new_db.as_dbc_string())

                messagebox.showinfo("Success", "DBC file saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save DBC file: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DBCEditor(root)
    root.mainloop()
