import os
import re
import argparse
from typing import List, Optional
from datetime import datetime
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('file_renamer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BulkFileRenamer:
    def __init__(self, directory: str):
        """
        Initialize the file renamer with the target directory.
        
        Args:
            directory: Path to the directory containing files to rename
        """
        self.directory = directory
        self.dry_run = False
        self.backup = False
        self.confirm_each = False
        self.max_filename_length = 255  # Standard filesystem limit

    def validate_directory(self) -> bool:
        """Check if the directory exists and is accessible."""
        try:
            if not os.path.exists(self.directory):
                logger.error(f"Directory does not exist: {self.directory}")
                return False
            if not os.path.isdir(self.directory):
                logger.error(f"Path is not a directory: {self.directory}")
                return False
            return True
        except Exception as e:
            logger.error(f"Error accessing directory: {e}")
            return False

    def get_files(self, recursive: bool = False) -> List[str]:
        """
        Get list of files in the directory.
        
        Args:
            recursive: Whether to include subdirectories
            
        Returns:
            List of file paths relative to the directory
        """
        files = []
        try:
            if recursive:
                for root, _, filenames in os.walk(self.directory):
                    for filename in filenames:
                        files.append(os.path.relpath(os.path.join(root, filename), self.directory))
            else:
                files = [f for f in os.listdir(self.directory) 
                         if os.path.isfile(os.path.join(self.directory, f))]
        except Exception as e:
            logger.error(f"Error listing files: {e}")
        return files

    def generate_new_name(self, filename: str, rules: dict) -> str:
        """
        Generate a new filename based on the specified rules.
        
        Args:
            filename: Original filename
            rules: Dictionary containing renaming rules
            
        Returns:
            New filename following the specified rules
        """
        try:
            path = Path(filename)
            name = path.stem
            ext = path.suffix.lower()

            # Apply text replacement (supports regex)
            if rules.get('replace_pattern') and rules.get('replacement'):
                if rules.get('use_regex', False):
                    name = re.sub(rules['replace_pattern'], rules['replacement'], name)
                else:
                    name = name.replace(rules['replace_pattern'], rules['replacement'])

            # Apply case conversion
            if rules.get('to_lowercase'):
                name = name.lower()
            elif rules.get('to_uppercase'):
                name = name.upper()
            elif rules.get('to_titlecase'):
                name = name.title()

            # Add prefix/suffix
            prefix = rules.get('prefix', '')
            suffix = rules.get('suffix', '')

            # Add sequence number if requested
            if rules.get('add_sequence'):
                sequence_format = rules.get('sequence_format', '_{:04d}')
                sequence = rules.get('current_sequence', 1)
                suffix += sequence_format.format(sequence)
                rules['current_sequence'] = sequence + 1

            # Add timestamp if requested
            if rules.get('add_timestamp'):
                timestamp_format = rules.get('timestamp_format', '_%Y%m%d_%H%M%S')
                suffix += datetime.now().strftime(timestamp_format)

            # Clean filename (remove special chars)
            if rules.get('clean_filename'):
                name = re.sub(r'[^\w\-_.]', '_', name)

            # Truncate if needed
            max_length = self.max_filename_length - len(prefix) - len(suffix) - len(ext)
            if len(name) > max_length:
                name = name[:max_length]
                logger.warning(f"Truncated filename: {filename}")

            new_name = f"{prefix}{name}{suffix}{ext}"
            return new_name
        except Exception as e:
            logger.error(f"Error generating new name for {filename}: {e}")
            return filename

    def rename_files(self, files: List[str], rules: dict) -> dict:
        """
        Perform the bulk rename operation.
        
        Args:
            files: List of files to rename
            rules: Dictionary containing renaming rules
            
        Returns:
            Dictionary with rename results and statistics
        """
        results = {
            'success': 0,
            'skipped': 0,
            'errors': 0,
            'renamed': [],
            'failed': []
        }

        if 'add_sequence' in rules:
            rules['current_sequence'] = rules.get('start_sequence', 1)

        for filename in files:
            try:
                old_path = os.path.join(self.directory, filename)
                new_name = self.generate_new_name(filename, rules)
                new_path = os.path.join(self.directory, new_name)

                # Skip if no change
                if filename == new_name:
                    results['skipped'] += 1
                    logger.info(f"Skipped (no change): {filename}")
                    continue

                # Check for conflicts
                if os.path.exists(new_path):
                    results['skipped'] += 1
                    logger.warning(f"Skipped (conflict): {filename} -> {new_name}")
                    results['failed'].append((filename, new_name, "File exists"))
                    continue

                # Dry run mode
                if self.dry_run:
                    results['skipped'] += 1
                    logger.info(f"Would rename: {filename} -> {new_name}")
                    results['renamed'].append((filename, new_name))
                    continue

                # Confirm each rename if enabled
                if self.confirm_each:
                    response = input(f"Rename '{filename}' to '{new_name}'? [y/n]: ").lower()
                    if response != 'y':
                        results['skipped'] += 1
                        logger.info(f"Skipped (user canceled): {filename}")
                        continue

                # Create backup if enabled
                if self.backup:
                    backup_path = os.path.join(self.directory, f"backup_{filename}")
                    os.rename(old_path, backup_path)
                    old_path = backup_path

                # Perform the rename
                os.rename(old_path, new_path)
                results['success'] += 1
                logger.info(f"Renamed: {filename} -> {new_name}")
                results['renamed'].append((filename, new_name))

            except Exception as e:
                results['errors'] += 1
                logger.error(f"Error renaming {filename}: {e}")
                results['failed'].append((filename, new_name, str(e)))

        return results

def main():
    """Command-line interface for the bulk file renamer."""
    parser = argparse.ArgumentParser(
        description='Enhanced Bulk File Renamer Tool',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Required arguments
    parser.add_argument('directory', help='Directory containing files to rename')
    
    # Renaming options
    parser.add_argument('-p', '--prefix', default='', help='Text to prepend to filenames')
    parser.add_argument('-s', '--suffix', default='', help='Text to append to filenames (before extension)')
    parser.add_argument('-r', '--replace', nargs=2, metavar=('OLD', 'NEW'), 
                        help='Text to replace in filenames')
    parser.add_argument('--regex', action='store_true', 
                        help='Use regex for text replacement')
    
    # Case conversion
    case_group = parser.add_mutually_exclusive_group()
    case_group.add_argument('--lower', action='store_true', help='Convert to lowercase')
    case_group.add_argument('--upper', action='store_true', help='Convert to uppercase')
    case_group.add_argument('--title', action='store_true', help='Convert to title case')
    
    # Additional features
    parser.add_argument('--seq', action='store_true', 
                        help='Add sequential numbers to filenames')
    parser.add_argument('--seq-start', type=int, default=1, 
                        help='Starting number for sequence')
    parser.add_argument('--seq-format', default='_{:04d}', 
                        help='Format string for sequence numbers')
    parser.add_argument('--timestamp', action='store_true', 
                        help='Add timestamp to filenames')
    parser.add_argument('--timestamp-format', default='_%Y%m%d_%H%M%S', 
                        help='Format string for timestamp')
    parser.add_argument('--clean', action='store_true', 
                        help='Remove special characters from filenames')
    
    # Operation modes
    parser.add_argument('--recursive', action='store_true', 
                        help='Include files in subdirectories')
    parser.add_argument('--dry-run', action='store_true', 
                        help='Show what would be renamed without making changes')
    parser.add_argument('--backup', action='store_true', 
                        help='Create backup copies of original files')
    parser.add_argument('--confirm', action='store_true', 
                        help='Confirm each rename interactively')
    
    # Logging
    parser.add_argument('--log-level', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help='Set the logging level')

    args = parser.parse_args()
    logger.setLevel(args.log_level)
    
    try:
        renamer = BulkFileRenamer(args.directory)
        if not renamer.validate_directory():
            return

        renamer.dry_run = args.dry_run
        renamer.backup = args.backup
        renamer.confirm_each = args.confirm

        # Prepare renaming rules
        rules = {
            'prefix': args.prefix,
            'suffix': args.suffix,
            'to_lowercase': args.lower,
            'to_uppercase': args.upper,
            'to_titlecase': args.title,
            'add_sequence': args.seq,
            'start_sequence': args.seq_start,
            'sequence_format': args.seq_format,
            'add_timestamp': args.timestamp,
            'timestamp_format': args.timestamp_format,
            'clean_filename': args.clean
        }

        if args.replace:
            rules.update({
                'replace_pattern': args.replace[0],
                'replacement': args.replace[1],
                'use_regex': args.regex
            })

        # Get files and perform renaming
        files = renamer.get_files(args.recursive)
        if not files:
            logger.warning("No files found to rename")
            return

        logger.info(f"Found {len(files)} files to process")
        results = renamer.rename_files(files, rules)

        # Print summary
        logger.info("\n=== Renaming Summary ===")
        logger.info(f"Successfully renamed: {results['success']}")
        logger.info(f"Skipped: {results['skipped']}")
        logger.info(f"Errors: {results['errors']}")

        if args.dry_run:
            logger.info("\nNOTE: Dry run mode - no files were actually renamed")

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()