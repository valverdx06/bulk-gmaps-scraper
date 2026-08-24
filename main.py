import argparse
import sys
from config import MAX_RESULTS_DEFAULT, DEFAULT_HEADLESS
from utils.logger import logger
from utils.exporter import export_data
from scraper.gmaps_scraper import GoogleMapsScraper

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Google Maps International Lead Generator & Web Intelligence Scraper"
    )
    parser.add_argument(
        "-c", "--category", type=str,
        help="Business category or industry type (e.g. 'Gyms', 'Dental Clinics', 'Lawyers')"
    )
    parser.add_argument(
        "-l", "--city", type=str,
        help="City or location (e.g. 'Madrid', 'Miami', 'Buenos Aires', 'São Paulo')"
    )
    parser.add_argument(
        "-C", "--country", type=str, default="",
        help="Country (Optional, e.g. 'Spain', 'USA', 'Argentina', 'Brazil')"
    )
    parser.add_argument(
        "-q", "--query", type=str,
        help="Direct search query override (e.g. 'Hotels in Barcelona, Spain')"
    )
    parser.add_argument(
        "-m", "--max-results", type=int, default=MAX_RESULTS_DEFAULT,
        help=f"Maximum number of leads to extract (Default: {MAX_RESULTS_DEFAULT})"
    )
    parser.add_argument(
        "--no-web-enrichment", action="store_true",
        help="Disable web crawling for emails and social media profiles"
    )
    parser.add_argument(
        "--headful", action="store_true",
        help="Run browser with visible graphical user interface"
    )
    return parser.parse_args()

def prompt_interactive() -> tuple[str, int, bool, bool]:
    """Interactively prompts user for search parameters if flags are omitted."""
    print("=" * 70)
    print(" 🚀 GOOGLE MAPS INTERNATIONAL LEAD GENERATOR & WEB ENRICHER 🚀")
    print("=" * 70)
    
    category = input("👉 Enter business category (e.g. Gyms, Dental Clinics): ").strip()
    city = input("👉 Enter city / state / country (e.g. Madrid, Miami, London): ").strip()
    
    query = f"{category} in {city}" if category and city else category or city
    
    max_res_str = input(f"👉 Maximum lead count [{MAX_RESULTS_DEFAULT}]: ").strip()
    max_results = int(max_res_str) if max_res_str.isdigit() else MAX_RESULTS_DEFAULT

    enrich_opt = input("👉 Enrich with web intelligence (Emails & Social Profiles)? (Y/n): ").strip().lower()
    extract_web_data = False if enrich_opt == 'n' else True

    return query, max_results, extract_web_data, DEFAULT_HEADLESS

def main():
    args = parse_arguments()

    if args.query:
        search_query = args.query
    elif args.category or args.city:
        parts = [p for p in [args.category, args.city, args.country] if p]
        search_query = " in ".join(parts) if len(parts) > 1 else parts[0]
    else:
        search_query, max_results, extract_web_data, headless = prompt_interactive()
        if not search_query:
            logger.error("At least one search parameter must be specified.")
            sys.exit(1)
        args.max_results = max_results
        args.no_web_enrichment = not extract_web_data
        args.headful = not headless

    headless = not args.headful
    extract_web_data = not args.no_web_enrichment

    logger.info(f"Target Query: '{search_query}'")
    logger.info(f"Max Results Limit: {args.max_results} | Headless Browser: {headless} | Web Intelligence Enrichment: {extract_web_data}")

    scraper = GoogleMapsScraper(headless=headless)
    results = scraper.scrape(
        query=search_query,
        max_results=args.max_results,
        extract_web_data=extract_web_data
    )

    if results:
        excel_file, csv_file = export_data(results, search_query)
        print("\n" + "=" * 70)
        print(" 🎉 LEAD EXTRACTION & ENRICHMENT COMPLETED SUCCESSFULLY! 🎉")
        print("=" * 70)
        print(f"📊 Total Qualified Leads Extracted: {len(results)}")
        print(f"📁 Enriched Excel File (.xlsx):    {excel_file}")
        print(f"📁 Enriched CSV File (.csv):      {csv_file}")
        print("=" * 70 + "\n")
    else:
        logger.warning("No lead results returned for the specified query.")

if __name__ == "__main__":
    main()
