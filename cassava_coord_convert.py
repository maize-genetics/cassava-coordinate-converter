# cassava_coord_convert.py
from shiny import App, render, ui, reactive
import subprocess
import tempfile
import os
from pathlib import Path
import pandas as pd

# Cassava chain file configurations - all .gz files
CASSAVA_CHAIN_CONFIGS = {
    "v6 → v7": {
        "filename": "Mesculenta_305_v6.to_v7.final.numeric.chain.gz",
        "local_path": "chain_files/Mesculenta_305_v6.to_v7.final.numeric.chain.gz"
    },
    "v6 → v8": {
        "filename": "Mesculenta_671_v8.0fromv6.0.final.chain.gz", 
        "local_path": "chain_files/Mesculenta_671_v8.0fromv6.0.final.chain.gz"
    },
    "v7 → v8": {
        "filename": "Mesculenta_671_v8.0fromv7.0.final.chain.gz",
        "local_path": "chain_files/Mesculenta_671_v8.0fromv7.0.final.chain.gz"
    }
}

def check_chain_files():
    """Check which chain files are available locally"""
    available_chains = {}
    
    for conversion, config in CASSAVA_CHAIN_CONFIGS.items():
        chain_path = config["local_path"]
        if Path(chain_path).exists():
            available_chains[conversion] = chain_path
            print(f"✅ Found: {conversion} ({config['filename']})")
        else:
            print(f"❌ Missing: {chain_path}")
    
    return available_chains

def run_crossmap(chain_file, input_data):
    """Run CrossMap conversion"""
    with tempfile.TemporaryDirectory() as temp_dir:
        input_file = Path(temp_dir) / "input.bed"
        output_file = Path(temp_dir) / "output.bed"
        
        # Write input as BED format
        input_file.write_text(input_data)
        
        try:
            # Run CrossMap - using CrossMap (not CrossMap.py)
            cmd = ["CrossMap", "bed", chain_file, str(input_file), str(output_file)]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if output_file.exists():
                output_content = output_file.read_text().strip()
                if output_content:
                    return {"success": True, "output": output_content}
                else:
                    return {"success": False, "error": "No valid conversion found - coordinate may not exist in target genome"}
            else:
                return {"success": False, "error": "No output file generated"}
                
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            return {"success": False, "error": f"CrossMap error: {error_msg}"}
        except FileNotFoundError:
            return {"success": False, "error": "CrossMap command not found. Please install: pip install crossmap"}

def get_chain_chromosome_format(conversion, user_chromosome):
    """Convert user chromosome format to match the specific chain file"""
    
    # Extract the number from user input (e.g., "Chromosome14" -> 14)
    try:
        chr_num = int(user_chromosome.replace("Chromosome", ""))
    except ValueError:
        return None
    
    # Different chain files use different formats
    if conversion == "v6 → v7":
        # v6→v7 chain file uses numeric format: "14", "15"
        return str(chr_num)
    elif conversion == "v6 → v8":
        # v6→v8 chain file uses zero-padded format: "Chromosome03", "Chromosome15"  
        return f"Chromosome{chr_num:02d}"
    elif conversion == "v7 → v8":
        # v7→v8 chain file uses regular format: "Chromosome15"
        return f"Chromosome{chr_num}"
    else:
        # Default: return as-is
        return user_chromosome

# Initialize chain files
print("🌿 Checking cassava chain files...")
AVAILABLE_CHAINS = check_chain_files()
print(f"✅ Ready with {len(AVAILABLE_CHAINS)} cassava genome conversions!")

if not AVAILABLE_CHAINS:
    print("⚠️  No chain files found. Please add your cassava chain files to the chain_files/ directory")

# UI - Cassava-themed
app_ui = ui.page_fluid(
    # Custom CSS for cassava theme
    ui.tags.head(
        ui.tags.title("🌿 Cassava Genomic Coordinate Converter"),
        ui.tags.style("""
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
            }
            .main-container {
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
            }
            .card {
                background: white;
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                padding: 40px;
                margin: 20px 0;
                border: 1px solid rgba(255,255,255,0.2);
            }
            .title {
                text-align: center;
                color: #2d5016;
                margin-bottom: 10px;
                font-size: 2.8em;
                font-weight: 700;
            }
            .subtitle {
                text-align: center;
                color: #5a7c3a;
                margin-bottom: 30px;
                font-size: 1.2em;
            }
            .cassava-info {
                background: linear-gradient(45deg, #8FBC8F, #9ACD32);
                color: white;
                padding: 20px;
                border-radius: 12px;
                margin: 20px 0;
                text-align: center;
            }
            .input-group {
                margin-bottom: 20px;
            }
            .btn-convert {
                background: linear-gradient(45deg, #228B22, #32CD32);
                color: white;
                border: none;
                padding: 14px 35px;
                border-radius: 8px;
                font-size: 18px;
                font-weight: 600;
                cursor: pointer;
                width: 100%;
                margin: 25px 0;
                transition: all 0.3s ease;
            }
            .btn-convert:hover {
                background: linear-gradient(45deg, #1e7b1e, #2eb82e);
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            .result-success {
                background: linear-gradient(135deg, #d4edda, #c3e6cb);
                color: #155724;
                padding: 25px;
                border-radius: 12px;
                border-left: 6px solid #28a745;
                margin: 25px 0;
            }
            .result-error {
                background: linear-gradient(135deg, #f8d7da, #f1b0b7);
                color: #721c24;
                padding: 25px;
                border-radius: 12px;
                border-left: 6px solid #dc3545;
                margin: 25px 0;
            }
            .coordinate-display {
                font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
                font-size: 20px;
                font-weight: bold;
                background: #f8f9fa;
                padding: 8px 12px;
                border-radius: 6px;
                display: inline-block;
                margin: 5px;
            }
            .chromosome-examples {
                color: #6c757d;
                font-size: 0.9em;
                margin-top: 5px;
            }
            .chain-info {
                background: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
                font-size: 0.9em;
                color: #6c757d;
            }
        """)
    ),
    
    ui.div(
        {"class": "main-container"},
        
        # Header
        ui.h1("🌿 Cassava Genomic Coordinate Converter", class_="title"),
        ui.p("Convert coordinates between cassava reference genome versions", class_="subtitle"),
        
        # Info panel
        ui.div(
            {"class": "cassava-info"},
            ui.h4("🧬 Available Cassava Conversions"),
            ui.p("v6 → v7 • v6 → v8 • v7 → v8"),
            ui.p("Chromosomes: Chromosome01 - Chromosome18")
        ),
        
        # Main conversion card
        ui.div(
            {"class": "card"},
            
            # Input row
            ui.row(
                ui.column(4,
                    ui.div(
                        {"class": "input-group"},
                        ui.input_text("chromosome", "Chromosome:", 
                                    value="Chromosome01", 
                                    placeholder="Chromosome01, Chromosome02, ..."),
                        ui.div("Format: Chromosome01 - Chromosome18", class_="chromosome-examples")
                    )
                ),
                ui.column(4,
                    ui.div(
                        {"class": "input-group"},
                        ui.input_numeric("position", "Position (1-based):", 
                                       value=1000000, 
                                       min=1,
                                       step=1),
                        ui.div("Enter position as-is (1-based)", class_="chromosome-examples")
                    )
                ),
                ui.column(4,
                    ui.div(
                        {"class": "input-group"},
                        ui.input_numeric("end_position", "End Position (optional):", 
                                       value=None, 
                                       min=1,
                                       step=1),
                        ui.div("For ranges only", class_="chromosome-examples")
                    )
                )
            ),
            
            # Conversion selector
            ui.div(
                {"class": "input-group"},
                ui.input_selectize("conversion", "Select Conversion:",
                                 choices=list(AVAILABLE_CHAINS.keys()) if AVAILABLE_CHAINS else ["No chain files found"],
                                 selected=list(AVAILABLE_CHAINS.keys())[0] if AVAILABLE_CHAINS else None)
            ),
            
            # Show which chain file is being used
            ui.output_ui("chain_file_info"),
            
            # Convert button
            ui.input_action_button("convert", "🔄 Convert Coordinate", 
                                 class_="btn-convert"),
            
            # Result area
            ui.output_ui("result_display")
        ),
        
        # Quick examples and setup info
        ui.div(
  	   {"class": "card"},
    	   ui.h4("🌿 How to Use:"),
           ui.tags.ol(
               ui.tags.li("Chromosome: Enter Chromosome01 (or 02, 03, ..., 18)"),
               ui.tags.li("Position: Enter 1500000 (any 1-based position)"), 
               ui.tags.li("End Position: Leave blank for single position, or enter end coordinate for ranges"),
               ui.tags.li("Select conversion: v6 → v7, v6 → v8, or v7 → v8"),
               ui.tags.li("Click Convert!")
            )
        )
    )
)

def server(input, output, session):
    
    @output
    @render.ui
    def chain_file_info():
        """Show which chain file will be used"""
        if input.conversion() and input.conversion() in CASSAVA_CHAIN_CONFIGS:
            filename = CASSAVA_CHAIN_CONFIGS[input.conversion()]["filename"]
            return ui.div(
                {"class": "chain-info"},
                f"📎 Using chain file: {filename}"
            )
        return ui.div()
    
    @output
    @render.ui
    @reactive.event(input.convert)
    def result_display():
        # Check if any chain files are available
        if not AVAILABLE_CHAINS:
            return ui.div(
                {"class": "result-error"},
                "❌ No cassava chain files found",
                ui.br(), ui.br(),
                "Please add the following files to the chain_files/ directory:",
                ui.tags.ul(
                    ui.tags.li("Mesculenta_305_v6.to_v7.final.numeric.chain.gz"),
                    ui.tags.li("Mesculenta_671_v8.0fromv6.0.final.chain.gz"),
                    ui.tags.li("Mesculenta_671_v8.0fromv7.0.final.chain.gz")
                )
            )
        
        # Validate inputs
        if not input.conversion() or not input.chromosome() or not input.position():
            return ui.div(
                {"class": "result-error"},
                "⚠️ Please fill in all required fields (Chromosome and Position)"
            )
        
        if input.conversion() not in AVAILABLE_CHAINS:
            return ui.div(
                {"class": "result-error"}, 
                f"❌ Conversion '{input.conversion()}' not available. Available: {', '.join(AVAILABLE_CHAINS.keys())}"
            )
        
        # Validate cassava chromosome format
        chromosome = input.chromosome().strip()
        if not chromosome.startswith("Chromosome"):
            return ui.div(
                {"class": "result-error"},
                "⚠️ Please use cassava chromosome format: Chromosome01, Chromosome02, ..., Chromosome18"
            )
        
        # Extract chromosome number and validate
        try:
            chr_num = int(chromosome.replace("Chromosome", ""))
            if chr_num < 1 or chr_num > 18:
                return ui.div(
                    {"class": "result-error"},
                    "⚠️ Cassava has 18 chromosomes. Please use Chromosome01 - Chromosome18"
                )
        except ValueError:
            return ui.div(
                {"class": "result-error"},
                "⚠️ Invalid chromosome format. Use: Chromosome01, Chromosome02, etc."
            )
        
        # Prepare coordinate
        position = int(input.position())
        end_pos = input.end_position()

        # Convert chromosome name for the specific chain file
        chr_for_chain = get_chain_chromosome_format(input.conversion(), chromosome)

        if not chr_for_chain:
            return ui.div(
                {"class": "result-error"},
                f"⚠️ Could not convert chromosome format for '{chromosome}'"
            )

        # Create BED format input (0-based coordinates for CrossMap)
        if end_pos and end_pos > position:
            bed_input = f"{chr_for_chain}\t{position-1}\t{end_pos}"
            original_display = f"{chromosome}:{position}-{end_pos}"
        else:
            bed_input = f"{chr_for_chain}\t{position-1}\t{position}"
            original_display = f"{chromosome}:{position}"
        
        # Get chain file
        chain_file = AVAILABLE_CHAINS[input.conversion()]
        chain_filename = CASSAVA_CHAIN_CONFIGS[input.conversion()]["filename"]
        
        # Run conversion
        result = run_crossmap(chain_file, bed_input)
        
        if result["success"]:
            # Parse result
            output_lines = [line for line in result["output"].split('\n') if line.strip()]
            
            if not output_lines:
                return ui.div(
                    {"class": "result-error"},
                    "❌ No conversion result - coordinate may not exist in target genome version"
                )
            
            output_line = output_lines[0]
            parts = output_line.split('\t')
            
            if len(parts) >= 3:
                new_chr = parts[0]
                new_start = int(parts[1]) + 1  # Convert back to 1-based for user
                new_end = int(parts[2])
                
                # Convert result back to user-friendly format (Chromosome##)
                if new_chr.isdigit():
                    # Convert numeric back to Chromosome format
                    display_chr = f"Chromosome{int(new_chr):02d}"
                elif new_chr.startswith("Chromosome") and len(new_chr) <= 12:
                    # Already in correct format, but ensure zero-padding
                    chr_num = new_chr.replace("Chromosome", "")
                    if chr_num.isdigit():
                        display_chr = f"Chromosome{int(chr_num):02d}"
                    else:
                        display_chr = new_chr
                else:
                    # Keep as-is for other formats
                    display_chr = new_chr
                
                # Format converted coordinate (back to 1-based)
                if new_end > new_start:
                    converted_display = f"{display_chr}:{new_start}-{new_end}"
                else:
                    converted_display = f"{display_chr}:{new_start}"
                
                return ui.div(
                    {"class": "result-success"},
                    ui.h4("✅ Cassava Coordinate Conversion Successful!"),
                    ui.p("🌿 ", ui.strong("Original: "), ui.span(original_display, class_="coordinate-display")),
                    ui.p("🎯 ", ui.strong("Converted: "), ui.span(converted_display, class_="coordinate-display")),
                    ui.hr(),
                    ui.p("📋 Copy this result:"),
                    ui.tags.code(converted_display, 
                                style="background: #e8f5e8; padding: 8px 15px; border-radius: 6px; font-size: 16px;"),
                    ui.br(), ui.br(),
                    ui.div(
                        {"class": "chain-info"},
                        f"Converted using: {chain_filename}"
                    )
                )
            else:
                return ui.div(
                    {"class": "result-error"},
                    "❌ Invalid conversion result format"
                )
        else:
            return ui.div(
                {"class": "result-error"},
                f"❌ Conversion failed: {result['error']}",
                ui.br(), ui.br(),
                "💡 This could mean:",
                ui.tags.ul(
                    ui.tags.li("The coordinate doesn't exist in the target genome version"),
                    ui.tags.li("The chromosome name format is incorrect"),
                    ui.tags.li("The chain file has an issue")
                ),
                ui.br(),
                f"Chain file used: {chain_filename}"
            )

# Create the app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run(port=8000, host="0.0.0.0")
