# Cassava Genomic Coordinate Converter

Web app for converting genomic coordinates between cassava reference genomes:
- v6 → v7
- v6 → v8  
- v7 → v8

## Usage

1. Enter your chromosome (in format like 1 - 18)
2. Enter position (e.g., 154119589) (1-based, do not convert into bed format)  
3. Optionally enter end position for ranges
4. Select conversion type (e.g., v6 → v8)
5. Click "Convert Coordinate"
6. Copy your result!

## Required Files

Place these cassava chain files in the `chain_files/` directory:
- `Mesculenta_305_v6.to_v7.final.numeric.chain`
- `Mesculenta_671_v8.0fromv6.0.final.chain.gz`
- `Mesculenta_671_v8.0fromv7.0.final.chain.gz`

## Local Development

```bash
pip install -r requirements.txt
python cassava_coord_convert.py
```

Visit: http://127.0.0.1:8000
(Note: Use 127.0.0.1 instead of localhost if localhost doesn't work)
