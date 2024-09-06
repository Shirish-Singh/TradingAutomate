from fpdf import FPDF, XPos, YPos
import pandas as pd
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TradingReportPDF(FPDF):
    def header(self):
        """
        Adds a default header to the PDF. Override this method to customize the header.
        """
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 10, 'Trading Report', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.ln(10)

    def add_title(self, title, level=1):
        """
        Adds a title or header to the PDF.

        :param title: The text of the title.
        :param level: The level of the title (1 for H1, 2 for H2, etc.).
        """
        font_sizes = {1: 14, 2: 12, 3: 10}
        font_size = font_sizes.get(level, 12)
        self.set_font('Helvetica', 'B', font_size)
        self.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
        self.ln(5)

    def add_line(self):
        """
        Adds a horizontal line separator to the PDF.
        """
        self.set_draw_color(0, 0, 0)  # Black color
        self.set_line_width(0.5)
        line_start = self.get_x()
        line_width = self.epw  # Effective page width
        y = self.get_y()
        self.line(line_start, y, line_start + line_width, y)
        self.ln(5)

    def add_paragraph(self, text):
        """
        Adds a paragraph of text to the PDF.

        :param text: The text content. Can be a string or a pandas DataFrame.
        """
        if text is None:
            text = "No data available."

        if isinstance(text, pd.DataFrame):
            text = text.to_string(index=False)

        if not isinstance(text, str):
            text = str(text)

        self.set_font('Helvetica', '', 10)
        self.multi_cell(0, 10, text)
        self.ln()

    def add_table(self, data, col_widths=None):
        """
        Adds a table to the PDF.

        :param data: A list of lists representing rows of the table.
        :param col_widths: A list of column widths. If None, widths are equally divided.
        """
        if not data:
            self.add_paragraph("No data available for the table.")
            return

        num_cols = len(data[0])
        if not col_widths:
            col_widths = [self.epw / num_cols] * num_cols  # Equal width for all columns

        self.set_font('Helvetica', '', 10)
        for row in data:
            for i, item in enumerate(row):
                self.cell(col_widths[i], 10, str(item), border=1)
            self.ln()
        self.ln(5)

    def add_image(self, image_path, width=180, height=100):
        """
        Adds an image to the PDF.

        :param image_path: The file path of the image.
        :param width: The width of the image in the PDF.
        :param height: The height of the image in the PDF.
        """
        if os.path.exists(image_path):
            try:
                self.image(image_path, w=width, h=height)
                self.ln(10)
            except Exception as e:
                logging.error(f"Error adding image {image_path}: {e}")
                self.add_paragraph(f"Error adding image: {image_path}")
        else:
            logging.warning(f"Image not found: {image_path}")
            self.add_paragraph(f"Image not found: {image_path}")

    def add_algorithm_section(self, algorithm_name, results):
        """
        Adds a section for an algorithm's results.

        :param algorithm_name: The name of the algorithm or pattern.
        :param results: The results to display, which can be a list, DataFrame, or image path.
        """
        self.add_title(algorithm_name, level=2)

        if isinstance(results, list):
            self.add_paragraph("Results:")
            self.add_table(results)
        elif isinstance(results, pd.DataFrame):
            self.add_paragraph("Results:")
            self.add_paragraph(results)
        elif isinstance(results, str) and results.endswith('.png'):
            self.add_image(results)
        else:
            self.add_paragraph(results)

        self.add_line()

    def finalize_report(self, output_path):
        """
        Saves the PDF report to the specified file path.

        :param output_path: The file path where the PDF will be saved.
        """
        try:
            self.output(output_path)
            logging.info(f"Report successfully saved to {output_path}")
        except Exception as e:
            logging.error(f"Error saving report: {e}")

