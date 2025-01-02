import fitz
import csv
import pandas as pd
import numpy as np

def print_all(thing, line_cap=False):
    with pd.option_context(
        "display.max_rows", None, "display.max_columns", None, "display.width", None
    ):
        if line_cap:
            with pd.option_context("display.max_colwidth", None):
                print(thing)
        else:
            print(thing)




def convert_page_table_to_csv(doc, page_index):
    word_df = pd.DataFrame(
        doc[page_index - 1].get_textpage().extractWORDS(),
        columns=["x0", "y0", "x1", "y1", "word", "block_no", "line_no", "word_no"],
    )
    word_df["x0"] = word_df["x0"].astype(int)
    word_df["x1"] = word_df["x1"].astype(int)
    word_df["y0"] = word_df["y0"].astype(int)
    word_df["y1"] = word_df["y1"].astype(int)
    # Find columns assuming a separation of 20 px = new column
    # Done like this because rolling doesn't support multiple columns

    word_df["x_group"] = (word_df["x0"] - word_df["x1"].shift(1).fillna(0)).abs() >= 10
    word_df["x_group"] = word_df["x_group"].cumsum()
    # Find rows using the fact that their top edge will be perfectly aligned

    word_df["y_group"] = (
        word_df["y0"].rolling(window=2).apply(lambda x: x.iloc[1] != x.iloc[0])
    )
    word_df["y_group"] = word_df["y_group"].cumsum()
    # Filter for just lines that only contain number characters.

    data = word_df.groupby("y_group").apply(
        lambda g: (
            g if all(all(x in "0123456789.–+" for x in y) for y in g["word"]) else None
        )
    )

    def convert_to_floats(g):
        # Convert to floats, keeping just x and y position

        if len(g) == 1:
            return (
                g.iloc[0]["x1"],
                g.iloc[0]["y0"],
                g.iloc[0]["word"].replace("–", "-"),
            )
        elif len(g) == 2:
            return (
                (  # Ensure x alignment position is consistent
                    g.iloc[0]["x1"]  # in 1.0 +3 use end of 1.0
                    if "+" in g.iloc[1]["word"] or "–" in g.iloc[1]["word"]
                    else g.iloc[1]["x1"]  # in 1 000 use end of 000
                ),
                g.iloc[0]["y0"],
                (
                    g.iloc[0]["word"].replace("–", "-")
                    + g.iloc[1]["word"].replace("+", "E+").replace("–", "E-")
                ),
            )
        else:
            print_all(g)
            raise ValueError

    data = pd.DataFrame(
        [*data.groupby("x_group").apply(convert_to_floats).values],
        columns=["x", "y", "v"],
    )
    # Filter out junk, mostly column headers

    data = data.groupby("x").apply(lambda g: g if len(g) > 2 else None)
    x_values = data["x"].unique()
    y_values = data["y"].unique()
    data = data.set_index(["x", "y"], drop=True)
    result = []
    for y in y_values:
        temp = []
        for x in x_values:
            try:
                temp.append(str(data.loc[x, y]["v"]))
            except KeyError:
                temp.append("")
        result.append(temp)
    # Some tables have a left aligned column, which causes a misalignment like this:
    # 1,,1,1
    # 2,,2,2
    # 3,3,,3
    # 4,4,,4
    # Fix things that look like that by removing the empties

    try:
        while 1:
            misalignments = list(set([x.index("") for x in result]))
            if (
                len(misalignments) == 2
                and abs(misalignments[0] - misalignments[1]) == 1
            ):
                [x.remove("") for x in result]
    except ValueError:
        pass
    return "\n".join([",".join(x) for x in result])



def write_tables_to_file():
    path = r"manual.pdf"
    doc: fitz.Document = fitz.Document(path)
    geometric_pages = np.arange(49, 84, 2)
    with open("isa_to_manual_fix.csv", "w") as fp:
        for page in geometric_pages:
            fp.write(convert_page_table_to_csv(doc, int(page)))

def parse_output_file_fix_notation():
    # fieldnames = ['geom_alt','geop_alt','t_k','t_c','p','d','g']
    with open("isa_to_manual_fix.csv") as fp:
        with open("isa_exponents_fixed.csv", "w") as fp_exp:
            fp_exp.write("geometric_altitude,geopotential_altitude,temperature_kelvin,temperature_centigrade,pressure,density,gravity\n")

            reader = csv.reader(fp, delimiter=',')
            exponents = {}        
            for i, row in enumerate(reader):
                row_new = []
                for j, value in enumerate(row):
                    if "E" in value:
                        value_split = value.split("E")
                        exponents.update({j: value_split[1]})
                    new_value = float()
                    if j in exponents:
                        new_value = float(value)
                        if "E" not in value:
                            new_value = float(str(value) +"E"+ str(exponents.get(j)))
                    else:
                        new_value = float(value)
                    row_new.append(new_value)
                row_string = ','.join(str(x) for x in row_new) + "\n"
                fp_exp.write(row_string)



def main():
    # Step 1 - Uncomment next line if you haven't completed this step before/don't have the manually fixed file.
    # write_tables_to_file()
    
    # Step 2 - Open new table file and manually fix rows that aren't added to new line (probably a better way to do this, but it was just a few rows to fix)
        # Also need to add a geopotential altitude to the row matching the 1000m geometrical altitude
    
    # Step 3 - Read File, parse like columns/values scientific notation per value, and remake the file
        # Didn't investigate too hard to fix, but pressures from 1050-1450 are off by two decimal places.
    parse_output_file_fix_notation()

if __name__ == '__main__':
    main()
