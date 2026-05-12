from input_reformat import reformat_cube_state
from cube_solver import solve_cube

'''
#solved cube, apply F move & this is what should look like captured
sample_captured_faces = {
    "blue": [ #white on top
        ["blue", "blue", "blue"],
        ["blue", "blue", "blue"],
        ["blue", "blue", "blue"]
    ],
    "green": [ #white on top
        ["green", "green", "green"],
        ["green", "green", "green"],
        ["green", "green", "green"]
    ],
    "orange": [ #white on top
        ["orange", "orange", "yellow"],
        ["orange", "orange", "yellow"],
        ["orange", "orange", "yellow"]
    ],
    "red": [    #white on top
        ["white", "red", "red"],
        ["white", "red", "red"],
        ["white", "red", "red"]
    ],
    "white": [  #blue on top  
        ["white", "white", "white"],
        ["white", "white", "white"],
        ["orange", "orange", "orange"] 
    ],
    "yellow": [ #green on top
        ["red", "red", "red"],
        ["yellow", "yellow", "yellow"],
        ["yellow", "yellow", "yellow"]
         
    ]
}
'''

sample_captured_faces = {
    "blue": [ #yellow on top
        ["white",  "white", "orange"],
        ["yellow", "blue",  "green"],
        ["green",  "orange","blue"]
    ],

    "green": [ #yellow on top
        ["red",    "green", "red"],
        ["orange", "green", "green"],
        ["orange", "white", "blue"]
    ],

    "orange": [ #yellow on top
        ["blue",  "red",    "red"],
        ["white", "orange", "orange"],
        ["white", "yellow", "white"]
    ],

    "red": [ #yellow on top
        ["yellow", "green", "yellow"],
        ["orange", "red",   "blue"],
        ["yellow", "red",   "blue"]
    ],

    "white": [ #blue on top
        ["orange", "white", "red"],
        ["blue",   "white", "blue"],
        ["orange", "red",   "yellow"]
    ],

    "yellow": [ #blue on top
        ["white",  "yellow", "green"],
        ["yellow", "yellow", "red"],
        ["green",  "blue",   "green"]
    ]
}

cube_string = reformat_cube_state(sample_captured_faces)

print("\n--- Full Cube String ---")
print(cube_string)

solution = solve_cube(cube_string)


print("\n--- Solve Instructions ---")
print(solution)