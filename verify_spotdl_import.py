try:
    from spotdl.types.song import Song
    print("✅ Imported Song")
except ImportError as e:
    print(f"❌ Song Import Error: {e}")

try:
    from spotdl.search.utils import get_search_results
    print("✅ Imported get_search_results")
except ImportError:
    try:
        from spotdl.search.song_gatherer import from_search_term
        print("✅ Imported from_search_term")
    except ImportError as e:
        print(f"❌ Search Import Error: {e}")

import pkgutil
import spotdl
print("SpotDL Modules:")
for importer, modname, ispkg in pkgutil.walk_packages(spotdl.__path__, "spotdl."):
    if "search" in modname or "provider" in modname:
        print(modname)
