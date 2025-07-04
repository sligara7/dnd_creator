// Test script to run in browser console
console.log('=== Browser Console Test ===');
console.log('1. Testing if startCreation is defined:', typeof startCreation);
console.log('2. Testing if testFunction is defined:', typeof testFunction);

if (typeof startCreation === 'function') {
    console.log('✅ startCreation function is available');
    
    // Test with simple concept
    document.getElementById('characterConcept').value = 'A brave human fighter';
    console.log('3. Set character concept input');
    
    // Try to call the function
    try {
        console.log('4. Attempting to call startCreation...');
        startCreation();
        console.log('✅ startCreation called successfully');
    } catch (error) {
        console.error('❌ Error calling startCreation:', error);
    }
} else {
    console.error('❌ startCreation function not found');
}

// Test if elements exist
console.log('5. Testing DOM elements:');
console.log('   - characterConcept input:', document.getElementById('characterConcept'));
console.log('   - step1 element:', document.getElementById('step1'));
console.log('   - step2 element:', document.getElementById('step2'));

// Test if clicking works
console.log('6. Testing button click:');
const button = document.querySelector('button[onclick="startCreation()"]');
console.log('   - Start button found:', !!button);
if (button) {
    console.log('   - Button onclick attribute:', button.getAttribute('onclick'));
}
