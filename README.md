# vesta_vectors.py

A Python 3 script to visualise the extent of atomic displacement - useful for *ab-initio* defect calculations.
Uses the [Vesta](http://jp-minerals.org/vesta/en/) file format, which can be generated from a number of other structure data file formats using the Vesta software.
The only dependancy outside of the Python standard Library is NumPy, which is included in [standard scientific Python distributions](https://scipy.org/install.html).

**Input**

Two Vesta files: one for the initial structure (before relaxation), and one for the final structure (after relaxation).

**Output**

A Vesta file that contains vectors connecting the initial and final atomic positions.

### Command line options
```
-f --filenames  
      description: vector colour (in RGB)
      default: [255,0,0]
```

### Example

Example input (`initial.vesta`, `final.vesta`) and output (`vectors.vesta`) data is contained in the `./data` folder.

``` python3 vesta_vectors.py -f ./data/initial.vesta ./data/final.vesta -ar 512 ```

This will generate the file `vectors.vesta`. The argument `-ar` is used because the final structure file has a vacancy defect; atom number 512 has been removed from the initial structure file. 
When the output file `vectors.vesta` is opened in Vesta, you will see the following:

.....

All the atoms and bonds are removed so that the vectors can be seen clearly.
It is easy to adjust the visuals via Vesta to produce something nicer:

### Warnings!
 - This script has not been extensively tested - use at your own risk and check that the final vectors make sense.
 - The atoms must appear in the same order in the initial and final vesta files (it is possible to specify which atoms have been added or removed, if any)
 - It is assumed that there has been no change in cell volume or shape.

### Bugs

If vesta_vectors.py is not behaving as you expect, please [raise an issue]().
